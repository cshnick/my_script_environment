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

    Q_SLOT void k2p_clipboard() {qDebug() << "TEST!!!";}
    Q_SLOT bool check_password() {return true;}

private:
    QString name_;
    QVariantMap variants_;
};

#endif // RESOLVER_H
