import * as Net from "net";

export class DPCClient {
  private transactionId: number;
  private socket: Net.Socket;
  private buffer: string;
  private error?: (e: any) => void;

  constructor(host?: string, port?: number) {
    const h = host ? host : "127.0.0.1";
    const p = port ? port : 40221;
    this.socket = new Net.Socket();
    this.socket.connect({ port: p, host: h }, () => {
      console.log('DPC client connected\n');
    });
    this.buffer = "";
    this.transactionId = 0;
  }

  public onData(callback: (d: any, error: boolean) => void, once?: boolean) {
    const internal = (s: string) => {
      this.buffer += s;
      if (this.countBuf("{") > 0 && this.countBuf("[") === this.countBuf("]")
      && this.countBuf("{") === this.countBuf("}")) {
        const response = JSON.parse(this.buffer.replace(/\n/gm, ""));
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

  public submit(command: string, args: any[]): void {
    this.socket.write(JSON.stringify({"verb": command, "tid": this.transactionId++, "arguments": args}) + "\n");
  }

  private countBuf(char: string): number {
    return this.buffer.split(char).length - 1;
  }
}
