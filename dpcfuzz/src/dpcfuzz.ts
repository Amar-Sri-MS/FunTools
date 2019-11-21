import * as fs from "fs";
import { fake, JsonSchema } from "typescript-json-schema-faker";
import { DPCClient } from "./dpcclient";

const args = process.argv;
const error = (m: string) => {
  process.stdout.write(m + "\n");
  process.exit(1);
};

if (args.length < 3) { error("Please specify FunOS command to fuzz"); }

const timeout = (() => {
  const index = args.indexOf("--timeout");
  if (index === -1) { return 3000; }
  if (!args[index + 1]) { error("Please provide timeout value"); }
  return Number(args[index + 1]);
})();

function any_items(depth: number): JsonSchema {
  const options = [
    {type: "number"},
    {type: "object", minProperties: 2},
    {type: "string"},
    {type: "null"},
    {type: "boolean"},
  ] as JsonSchema[];
  if (depth > 0) {
    options.push({type: "array", items: any_items(depth - 1)});
  }
  return {anyOf: options} as JsonSchema;
}

function prepare(input: any): JsonSchema {
  if (typeof input === "string") {
    return prepare({type: input});
  }
  if (input.oneOf) {
    input.oneOf = prepare(input.oneOf);
  }
  if (input.anyOf) {
    input.anyOf = prepare(input.anyOf);
  }
  if (input.allOf) {
    input.allOf = prepare(input.allOf);
  }
  if (input.not) {
    input.not = prepare(input.not);
  }
  if (Array.isArray(input)) {
    return input.map(prepare);
  }
  if (input.items) {
    input.items = prepare(input.items);
  }
  if (input.type === "array" && !input.items) {
    input.items = any_items(3);
  }
  if (input.type === "object" && !input.minProperties) {
    input.minProperties = 2;
  }
  return input;
}

const verb = args[2];
const client = new DPCClient();
client.submit("schema", [verb]);
client.onTimeout(timeout, () => {
  error("Failed to get schema");
});
client.onData((schema: any, err: boolean) => {
  if (err) {
    error("Can't get schema for command to fuzz");
  }

  const preprocessed = prepare(schema);
  let request: any = {};
  const faker = () => {
    request = fake(preprocessed);
    client.submit(verb, request);
  };
  client.onData(faker);
  client.onError(() => {
    error("Crashed on " + JSON.stringify(request));
  });
  client.onTimeout(timeout, () => {
    error("Hanged on " + JSON.stringify(request));
  });
  faker();
}, true);
