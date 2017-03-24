#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickItem>
#include <QQuickWindow>
#include "resolver.h"
#include <QtNetwork>


int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;
    //qmlRegisterUncreatableType<Resolver>("PyResolver", 1, 0, "Resolver", QStringLiteral("The Resolver"));
    qmlRegisterType<Resolver>("PyResolver", 1, 0, "Resolver");
    engine.load(QUrl(QStringLiteral("qrc:/main.qml")));
    QQuickWindow *mwn = static_cast<QQuickWindow*>(engine.rootObjects().at(0));
    mwn->show();
    return app.exec();
}
