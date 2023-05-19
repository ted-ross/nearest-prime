SIZE := 2

prepare:
	which ansible || ( echo "ansible is not installed" && exit 1 )
	which ansible-galaxy || ( echo "ansible-galaxy is not installed" && exit 1 )
	ansible-galaxy install -r ansible/requirements.yml

setup: prepare
	ansible-playbook -i ansible/inventory-nearestprime-demo.yml ansible/setup/setup.yml

teardown: prepare
	ansible-playbook -i ansible/inventory-nearestprime-demo.yml ansible/teardown/teardown.yml

monitordb:
	ansible-playbook -i ansible/inventory-nearestprime-demo.yml ansible/db/monitor.yml

load-gen-start:
	ansible-playbook -i ansible/inventory-nearestprime-demo.yml ansible/load-gen/start.yml -e load_gen_size=$(SIZE)

load-gen-stop:
	ansible-playbook -i ansible/inventory-nearestprime-demo.yml ansible/load-gen/stop.yml
