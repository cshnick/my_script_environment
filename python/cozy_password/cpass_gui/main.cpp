#include <QApplication>
#include <QQmlApplicationEngine>
#include "resolver.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    QQmlApplicationEngine engine;
    qmlRegisterUncreatableType<Resolver>("PyResolver", 1, 0, "Resolver", QStringLiteral("The Resolver"));
    engine.load(QUrl(QStringLiteral("qrc:/main.qml")));

    return app.exec();
}
