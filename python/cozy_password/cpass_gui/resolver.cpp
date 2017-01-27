#include "resolver.h"

Resolver::Resolver(QObject *parent) : QObject(parent)
{
    variants_.insert("ncomputing", "password1");
    variants_.insert("zeropc", "passsdsgsdg");
    variants_.insert("shared", "leveelga");
    variants_.insert("skype", "gurazh");
    variants_.insert("facebook", "swarmhost");
}
