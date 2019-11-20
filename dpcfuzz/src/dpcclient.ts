import * as Net from "net";

export class DPCClient {
  private transactionId: number;
  private socket: Net.Socket;
  private buffer: string;
  private error?: (e: any) => void;
  private timeout_function?: () => void;
  private timeout?: ReturnType<typeof setTimeout>;
  private timeout_ms: number;

  constructor(host?: string, port?: number) {
    const h = host ? host : "127.0.0.1";
    const p = port ? port : 40221;
    this.socket = new Net.Socket();
    this.socket.connect({ port: p, host: h }, () => {
      process.stdout.write("DPC client connected\n");
    });
    this.socket.on("close", () => {process.stdout.write("DPC client disconnected\n")});
    this.buffer = "";
    this.transactionId = 0;
    this.timeout_ms = 0;
  }

  public onData(callback: (d: any, error: boolean) => void, once?: boolean) {
    const internal = (s: string) => {
      this.buffer += s;
      if (this.countBuf("{") > 0 && this.countBuf("[") === this.countBuf("]")
      && this.countBuf("{") === this.countBuf("}")) {
        if (this.timeout) {
          clearTimeout(this.timeout);
          this.timeout = undefined;
        }
        const response = JSON.parse(this.buffer);
        if (!response && this.error) this.error("No result");
        if (!response["result"]) {
          callback(response, true);
        } else {
          callback(response["result"], false);
        }
        this.buffer = "";
        if (once && once === true) {
          this.socket.off("data", internal);
        }
      }
    };
    this.socket.on("data", internal);
  }

  public onError(callback: (e: any) => void) {
    this.error = callback;
    this.socket.on("error", callback);
  }

  public onTimeout(ms: number, callback: () => void) {
    this.timeout_ms = ms;
    this.timeout_function = callback;
    this.socket.setTimeout(ms, callback);
  }

  public submit(command: string, args: any[], raw?: boolean): void {
    if (this.timeout_ms != 0 && this.timeout_function) {
      this.timeout = setTimeout(this.timeout_function, this.timeout_ms);
    }
    const a : any[] = (raw && raw === true) ? args : args.map(this.quote, this);
    this.socket.write(JSON.stringify({"verb": command, "tid": this.transactionId++, "arguments": a}) + "\n");
  }

  public end(): void {
    this.socket.end();
  }

  private countBuf(char: string): number {
    return this.buffer.split(char).length - 1;
  }

  private quote(a: any): any {
    if (Array.isArray(a)) {
      return ["quote", a.map(this.quote, this)];
    }
    if (a instanceof Object) {
      const result: any = {}
      for (const k in a) {
        result[k] = this.quote(a[k]);
      }
      return result;
    }
    return a;
  }
}
