import * as Net from "net";

export class DPCClient {
  private transactionId: number;
  private socket: Net.Socket;
  private buffer: string;
  private connected: boolean;
  private sendBuffer: string;
  private timeoutFunction?: () => void;
  private timeout?: ReturnType<typeof setTimeout>;
  private msTimeout: number;

  constructor(host?: string, port?: number) {
    const h = host ? host : "127.0.0.1";
    const p = port ? port : 40221;
    this.connected = false;
    this.sendBuffer = "";
    this.socket = new Net.Socket();
    this.socket.connect({ port: p, host: h }, () => {
      process.stdout.write("DPC client connected\n");
      this.connected = true;
      if (this.sendBuffer.length > 0) {
        this.socket.write(this.sendBuffer);
        this.sendBuffer = "";
      }
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
        if (!response || !response.result) {
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
    const message = JSON.stringify({verb: command, tid: this.transactionId++, arguments: a}) + "\n";
    if (this.connected) {
      this.socket.write(message);
    } else {
      this.sendBuffer += message;
    }
  }

  public end(): void {
    this.socket.end();
  }

  private quote(a: any): any {
    if (Array.isArray(a)) {
      return ["quote", a.map(this.quote, this)];
    }
    return a;
  }
}
