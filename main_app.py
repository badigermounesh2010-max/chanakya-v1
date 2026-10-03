from main import ChanakyaApp

if __name__ == '__main__':
    import asyncio
    app = ChanakyaApp()
    asyncio.run(app.get_status())
