import * as Net from "net";

export class DPCClient {
  private transactionId: number;
  private socket: Net.Socket;
  private buffer: string;
  private error?: (e: any) => void;
  private timeoutFunction?: () => void;
  private timeout?: ReturnType<typeof setTimeout>;
  private msTimeout: number;

  constructor(host?: string, port?: number) {
    const h = host ? host : "127.0.0.1";
    const p = port ? port : 40221;
    this.socket = new Net.Socket();
    this.socket.connect({ port: p, host: h }, () => {
      process.stdout.write("DPC client connected\n");
    });
    this.socket.on("close", () => {process.stdout.write("DPC client disconnected\n"); });
    this.buffer = "";
    this.transactionId = 0;
    this.msTimeout = 0;
  }

  public onData(callback: (d: any, error: boolean) => void, once?: boolean) {
    const internal = (s: string) => {
      this.buffer += s;
      try {
        const response = JSON.parse(this.buffer);
        if (this.timeout) {
          clearTimeout(this.timeout);
          this.timeout = undefined;
        }
        if (!response && this.error) { this.error("No result"); }
        if (!response.result) {
          callback(response, true);
        } else {
          callback(response.result, false);
        }
        this.buffer = "";
        if (once && once === true) {
          this.socket.off("data", internal);
        }
      } catch (e) {
        // it means the json is incomplete, wait for more
      }
    };
    this.socket.on("data", internal);
  }

  public onError(callback: (e: any) => void) {
    this.error = callback;
    this.socket.on("error", callback);
  }

  public onTimeout(ms: number, callback: () => void) {
    this.msTimeout = ms;
    this.timeoutFunction = callback;
    this.socket.setTimeout(ms, callback);
  }

  public submit(command: string, args: any[], raw?: boolean): void {
    if (this.msTimeout !== 0 && this.timeoutFunction) {
      this.timeout = setTimeout(this.timeoutFunction, this.msTimeout);
    }
    const a: any[] = (raw && raw === true) ? args : args.map(this.quote, this);
    this.socket.write(JSON.stringify({verb: command, tid: this.transactionId++, arguments: a}) + "\n");
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
    return a;
  }
}
