from flansible import app, config

if __name__ == '__main__':
    app.run(
        debug=True,
        host=config.get(
            "Default",
            "Flask_tcp_ip"
        ),
        use_reloader=True,
        port=int(config.get("Default", "Flask_tcp_port"))
    )
