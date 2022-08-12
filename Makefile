build:
	DOCKER_BUILDKIT=1 docker build -t subformula_graph_app . 

run:
	docker run -p 8050:8050 subformula_graph_app 