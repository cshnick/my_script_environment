#ifndef RESOLVER_H
#define RESOLVER_H

#include <QObject>
#include <QVariantList>

class Resolver : public QObject
{
    Q_OBJECT
public:
    explicit Resolver(QObject *parent = 0);

    Q_INVOKABLE QVariantList keys(const QString &/*criterion*/) {return QVariantList();}

signals:

public slots:
};

#endif // RESOLVER_H
