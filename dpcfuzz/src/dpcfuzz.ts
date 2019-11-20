import * as fs from "fs";
import { fake, JsonSchema } from "typescript-json-schema-faker";
import { DPCClient } from "./dpcclient";

const args = process.argv;

if (args.length < 3) {
  process.stdout.write("Please specify FunOS command to fuzz.\n");
  process.exit(1);
}

function any_items(depth: number): JsonSchema {
  const any = [
    {"type": "number"},
    {"type": "object", "minProperties": 2},
    {"type": "string"},
    {"type": "null"},
    {"type": "boolean"}
  ] as JsonSchema[];
  if (depth > 0) {
    any.push({"type": "array", "items": any_items(depth - 1)});
  }
  return {"anyOf": any} as JsonSchema;
}

function prepare(input: any): JsonSchema {
  if (typeof input === 'string') {
    return prepare({"type": input});
  }
  if (Array.isArray(input)) {
    return input.map(prepare);
  }
  if (input['items']) {
    input['items'] = prepare(input['items']);
  }
  if (input['type'] == 'array' && !input['items']) {
    input['items'] = any_items(3);
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

