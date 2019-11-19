import * as fs from "fs";
import { fake, JsonSchema } from "typescript-json-schema-faker";
import { DPCClient } from "./dpcclient";

const args = process.argv;

if (args.length < 3) {
  process.stdout.write("Please specify FunOS command to fuzz.\n");
  process.exit(1);
}

function prepare(input: any): JsonSchema {
  if (typeof input === 'string') {
    return {"type": input } as JsonSchema;
  }
  if (Array.isArray(input)) {
    return input.map(prepare);
  }
  if (input['items']) {
    input['items'] = prepare(input['items']);
  }
  return input;
}

const verb = args[2];
const client = new DPCClient();
client.submit("schema", [verb]);
client.onData((schema: any, error: boolean) => {
  if (error) {
    throw new Error("Can't get schema for command to fuzz");
  }

  const preprocessed = prepare(schema);
  let request: any = {};
  const faker = () => {
    request = fake(preprocessed);
    client.submit(verb, request);
  }
  client.onData(faker);
  client.onError(() => {
    throw new Error("Crashed on " + JSON.stringify(request));
  });
  faker();
}, true);

