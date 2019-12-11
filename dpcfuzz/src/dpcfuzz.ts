import { fake, JsonSchema } from "typescript-json-schema-faker";
import * as yargs from "yargs";
import { DPCClient } from "./dpcclient";

const error = (m: string) => {
  process.stdout.write(m + "\n");
  process.exit(1);
};
const success = (m: string) => {
  process.stdout.write(m + "\n");
  process.exit(0);
};

const argParser = yargs.command("[verb]", "DPC verb to fuzz")
.help("h").alias("h", "help").options({
H: { alias: "host", default: "127.0.0.1",
    describe: "DPC server to connect" , type: "string"},
l: { alias: "limit", default: -1,
    describe: "Limit the number of requests to run", type: "number" },
p: { alias: "port", default: 40221,
    describe: "DPC port to connect", type: "number" },
r: { alias: "random", default: false,
    describe: "Take random verb from help", type: "boolean" },
t: { alias: "timeout", default: 3000,
    describe: "Timeout for a single request", type: "number" }});
const argv = argParser.argv;

if (argv._.length === 0 && !argv.r) {
  argParser.showHelp();
  process.exit(1);
}

const timeout = argv.t;
const limit = argv.l;

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
  if (input.type === "object" && input.properties) {
    const result: any = {};
    for (const k of Object.keys( input.properties)) {
      result[k] = prepare(input.properties[k]);
    }
    input.properties = result;
  }
  return input;
}

const client = new DPCClient(argv.H, argv.p);

function fuzzVerb(verb: string): void {
  let iterationsPassed: number = 0;
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
      if (limit !== -1 && iterationsPassed >= limit) {
        success("Successfully ran " + String(iterationsPassed) + " requests");
      }
      request = fake(preprocessed);
      client.submit(verb, request);
      iterationsPassed++;
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
}

if (argv._.length === 1) {
  fuzzVerb(argv._[0]);
} else {
  client.submit("help", []);
  client.onTimeout(timeout, () => {
    error("Failed to get help");
  });
  client.onData((verbs: any, err: boolean) => {
    if (err) {
      error("Can't run help to list verbs");
    }
    const l = Object.keys(verbs);
    fuzzVerb(l[Math.floor(Math.random() * l.length)]);
  }, true);
}
