package io.skupper.restclient;

import javax.annotation.PostConstruct;
import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import java.util.LinkedList;

import io.vertx.axle.ext.web.client.WebClient;
import io.vertx.axle.core.Vertx;
import io.vertx.ext.web.client.WebClientOptions;

@Path("/set_load")
public class LoadGen {

    int concurrency = 0;
    int inFlight    = 0;
    int dbsize      = 10000;
    int total       = 0;
    int failures    = 0;
    String lastStatus = "<none>";

    LinkedList<Integer> worklist = new LinkedList<Integer>();

    @Inject
    Vertx vertx;

    private WebClient client;

    @PostConstruct
    void initialize() {
        client = WebClient.create(vertx,
            new WebClientOptions()
                .setDefaultHost("nearestprime")
                .setDefaultPort(8000));
        for (int i = 0; i < dbsize; i++) {
            worklist.addLast(i);
        }
    }

    private void sendRequest() {
        if (worklist.isEmpty()) {
            return;
        }
        inFlight++;
        int index = worklist.removeFirst();
        client.get(String.format("/post_work?id=%d", index))
            .send()
            .whenComplete((resp, exception) -> {
                inFlight--;
                if (exception == null) {
                    lastStatus = resp.statusMessage();
                    total++;
                } else {
                    failures++;
                    worklist.addFirst(index);
                }
                if (inFlight < concurrency) {
                    sendRequest();
                }
            });
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    @Path("/{val}")
    public String setLoad(@PathParam("val") String val) {
        int newVal;
        try {
            newVal = Integer.parseInt(val);
        } catch (Exception e) {
            newVal = concurrency;
        }

        concurrency = newVal;

        while (concurrency > inFlight && !worklist.isEmpty()) {
            sendRequest();
        }

        return String.format("Load set to %d (in-flight: %d, completed: %d, retries: %d, last_status: %s)",
            concurrency, inFlight, total, failures, lastStatus);
    }
}

