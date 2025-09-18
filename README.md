# rdf2flymine

## Working
The script contains 3 classes:
* Rdf2ShEx. It can mine a SPARQL endpoint to generate shape for every class with instances. Mainly a wrapper of sheXer adapted to this use case.
* ShEx2Flymine. It gets a ShEx schema and maps it to FlyMine's model.json structure.
* Rdf2Flymine. It combines the previous two to go all the way from data exposed in a SPARQL endpoint to model.json

## TO-DOs
* Fill packages. Choosing manually a value?)
* Fill terms. Are examples of nodes among the data? If so, sheXer can cacth those and write them down in annotations that can be parsed with pyShex.
* Fill reverseReference. Using ontology information?
* Fill counts. sheXer can count instances, but it won't work against endpoint. Better use ad-hoc sparql queries.
* Improve selection of entities to be taken as example. Can be done with extra queries and then feeding sheXer with a shape map targetting custom nodes rather than using all_classes_mode.
* Improce display name generation if possible using ontology information.
* Fill executionTime. ??
* Fill wasSuccesful. ??
* Fill error. ??
* Fill statusCode. ??
* Fill isInterface. ??
* Fill tags. ??
