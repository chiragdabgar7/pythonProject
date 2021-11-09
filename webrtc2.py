from aiohttp import web
from rtcbot import RTCConnection, getRTCBotJS

routes = web.RouteTableDef()

# For this example, we use just one global connection
conn = RTCConnection()


@conn.subscribe
def onMessage(msg):
    print("Got Message :", msg)


# Server the RTCBOT javascript library in rtcbot.js
@routes.get("/rtcbot.js")
async def rtcbotjs(request):
    return web.Response(content_type="application/javascript", text=getRTCBotJS())


# This sets up the connection
@routes.get('/')
async def index(request):
    return web.Response(
        content_type="text/html",
        text="""
        <html>
            <head>
                <title>RTCBot: Data Channel</title>
                <script src="/rtcbot.js"></script>
            </head>
            <body style="text-align: center;padding-top: 30px;">
                <h1>Click the Button</h1>
                <button type="button" id="mybutton">Click me!</button>
                <p>
                Open the browser's developer tools to see console messages (CTRL+SHIFT+C)
                </p>
                <script>
                    var conn = new rtcbot.RTCConnection();

                    async function connect() {
                        let offer = await conn.getLocalDescription();

                        // POST the information to /connect
                        let response = await fetch("/connect", {
                            method: "POST",
                            cache: "no-cache",
                            body: JSON.stringify(offer)
                        });

                        await conn.setRemoteDescription(await response.json());

                        console.log("Ready!");
                    }
                    connect();


                    var mybutton = document.querySelector("#mybutton");
                    mybutton.onclick = function() {
                        conn.put_nowait("Button Clicked!");
                    };
                </script>
            </body>
        </html>
        """)


async def cleanup(app=None):
    await conn.close()

app = web.Application()
app.add_routes(routes)
app.on_shutdown.append(cleanup)
web.run_app(app)
