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
    Q_PROPERTY(QString password READ password WRITE setPassword NOTIFY passwordChanged)
public:
    explicit Resolver(QObject *parent = 0);

    QString name() {return name_;}
    void setName(const QString &name) {name_ = name;}

    QStringList keys() {return variants_.keys();}
    QString password() { return password_;}
    void setPassword(const QString &value) {password_ = value; Q_EMIT(passwordChanged(value));}

    Q_SIGNAL void nameChanged(const QString &newname);
    Q_SIGNAL void keysChanged(const QStringList &newkeys);
    Q_SIGNAL void passwordChanged(const QString &password);

    Q_SLOT bool contains(const QString &text) {return variants_.keys().contains(text);}
    Q_SLOT void k2p_clipboard(const QString &str) {qDebug() << "TEST!!! " << str;}
    Q_SLOT bool check_password(const QString &param) {return !param.compare("rbhpf");}
    Q_SLOT bool new_entry(const QString &/*key*/, const QString &/*password*/) {return false;}
    Q_SLOT bool set(const QString &/*key*/, const QString &/*password*/) {return true;}
    Q_SLOT bool del(const QString &/*key*/) {return true;}
    Q_SLOT bool rename(const QString &/*old_name*/, const QString &/*new_name*/) {return true;}
    Q_SLOT void sync() {Q_EMIT(keysChanged(variants_.keys()));}

private:
    QString name_;
    QVariantMap variants_;
    QString password_ = "rbhpf";
};

#endif // RESOLVER_H
