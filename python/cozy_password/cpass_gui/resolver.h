#ifndef RESOLVER_H
#define RESOLVER_H

#include <QObject>
#include <QVariantList>
#include <QDebug>

class Resolver : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString name READ name WRITE setName NOTIFY nameChanged)
    Q_PROPERTY(QStringList keys READ keys NOTIFY keysChanged)
public:
    explicit Resolver(QObject *parent = 0);

    QString name() {return name_;}
    void setName(const QString &name) {name_ = name;}

    QStringList keys() {return variants_.keys();}

    Q_SIGNAL void nameChanged(const QString &newname);
    Q_SIGNAL void keysChanged(const QStringList &newKey);

    Q_SLOT bool contains(const QString &text) {return variants_.keys().contains(text);}
    Q_SLOT void k2p_clipboard(const QString &str) {qDebug() << "TEST!!! " << str;}
    Q_SLOT bool check_password(const QString &param) {return !param.compare("rbhpf");}
    Q_SLOT void sync() {;}

private:
    QString name_;
    QVariantMap variants_;
};

#endif // RESOLVER_H
