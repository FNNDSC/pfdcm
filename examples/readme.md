
Now you'll need to initialize PFDCM to use it as an API for ChRIS UI. Either follow the instructions in [workflow.sh](../pfdcm/workflow.sh) or use a REST client like [Insomnia](https://insomnia.rest/) (a [request collection file](./examples/Insomnia.yaml) is provided, import this) or PostMan.

- Initialize the xinetd listener. Simply use the default.
- Register a PACS service, orthanc in our case. Make sure that the `serverIP` field matches exactly with the IP address of your machine that you put in `orthanc.json` in a previous step.
- Register a local CUBE and a local Swift. The `"cubeKeyName"` and `"swifteyName"` that you provide here will be used in setting up ChRIS_ui.
- Test by performing a find query.

