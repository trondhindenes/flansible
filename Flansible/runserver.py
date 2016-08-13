from flansible import app, config
import platform
#Visual studio remote debugger
if platform.node() == 'mgmt':
    try:
        import ptvsd
        ptvsd.enable_attach(secret='my_secret', address = ('0.0.0.0', 3000))
    except:
        pass

if __name__ == '__main__':
    app.run(debug=True, host=config.get("Default", "Flask_tcp_ip"), use_reloader=False, port=int(config.get("Default", "Flask_tcp_port")))