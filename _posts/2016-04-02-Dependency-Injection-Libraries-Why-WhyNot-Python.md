---
layout: post
title: Dependency Injection libraries, why and why not use them with Python
---

Recently the DI pattern has appeard in front of me as a design pattern, no matters how but it
challenged me. In this post I want to review the usage of the DI pattern and compare it with more
traditional patterns such as the global class pattern.

I have never been keen on design patterns as a programmer, not beause I thing this is not
a iteresting field, I guess the subject by it self never caughtes me instead of other fields. My short knowledge about
design patterns is thanks to those friends that I have had the opportunity to work with them, and
sometimes their teaching has challenged me to improve me in the design patterns field.

There are a lot of literature about DI and IoC over there, from this magnifique [post](//martinfowler.com/articles/injection.html) 
by Martin Flowers till good [threads](//stackoverflow.com/questions/130794/what-is-dependency-injection) in stackoverflow.
But Im keen on move the conversation in the Python context and the use of DI libraries, where they are not fully used by the most of projects and community.

## The DI library and implicitly

The following snippet shows the code that challenge me. It uses a [DI library](//stackoverflow.com/questions/130794/what-is-dependency-injection) 
that takes benefeit of the Python. It helps the developer injecting the dependencies to the functions using
decorators. It has support for other mechanisms such as metaclasses and protocol descriptors, but we will leave them aside.

{% highlight python %}
from di import injector, Key, DependencyMap

from mylogging import Logger

dm = DependencyMap()
MyLogger = Key('logger')

@dm.singleton(MyLogger)
def mylogger(dm):
    return Logger()

inject = injector(dm)

@inject
def sum(x, y, logger=MyLogger):
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

@inject
def main(logger=MyLogger):
    logger.debug("Sum program executed")
    logger.info(sum(2, 3))

if __name__ == "__main__":
    main()
{% endhighlight python %}

The *inject* as a decorator wires automatically our *main* function with the same instance of our logger class. This allows to the
functions that use the *logger* classs do not worry about how to build it, hence it makes the code lessly coupled.

We can se how the dependency passing argument becomes implicitly due the use of the library. In the following but, the code does the same
but it makes it explicity, as the dependency injection pattern defines when it uses the parameter passing way.

{% highlight python %}
from .logging import Logger

def sum(logger)
    logger.debug("Sum {} and {}".format(x, y))
    return x + y 

def main(logger)
    logger.info("Sum program executed")
    sum(2, 3)

if __name__ == "__main__":
    logger = Logger()
    main(logger)
{% endhighlight python %}

Both cases remove the factory pattern used by the following code, where it leaves the code very coupled and tied. If we want to change
the constructor of the *Logger* class we must modify the whole code where this class is instanciated.

{% highlight python %}
from mylogging import Logger

def sum(x, y):
    logger = Logger()
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

def main():
    logger = Logger()
    logger.debug("Sum program executed")
    logger.info(sum(2, 3))

if __name__ == "__main__":
    main()
{% endhighlight python %}

This code is also affected by a issue raised because of the global state, if we execute the command the result appears twice in the console. We will face it later.

## Tunning the logging instance verbosity

Following the previous example we want to add a new param to the *Logger* intance to decide which level of verbosity the program
will have, to make that we are going to use a command option flag to configure the level desired. To simplify the scenario we will
just take into consideration two verbose levels : *debug* and *info*.

Leaving for a while the factory pattern that we used before, we are going to start seeing the proper way to do that with the dependency injection 
pattern with no use of DI libraries, the following code shows it:

{% highlight python %}
import sys
from mylogging import Logger

def sum(x, y, logger):
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

def main(logger):
    logger.debug("Sum program executed")
    logger.info(sum(2, 3, logger))

if __name__ == "__main__":
    try:
        debug = True if sys.argv[1] == '-v' else False
    except IndexError:
        debug = False

    logger = Logger(debug=debug)
    main(logger)
{% endhighlight python %}

The code wires the functions with the instance class configured with the proper debug level. All functions that use this instance will
behave as we exepected regarding the logging mechanism. 

Now lets we are going to modify the code that uses the DI library, the following code injects the *Logger* instance that was configured with
the debug level.

{% highlight python %}
import sys

from di import injector, Key, DependencyMap

from mylogging import Logger

dm = DependencyMap()
MyLogger = Key('logger')

@dm.singleton(MyLogger)
def mylogger(dm):
    try:
        debug = True if sys.argv[1] == '-v' else False
    except IndexError:
        debug = False
    return Logger(debug=debug)

inject = injector(dm)

@inject
def sum(x, y, logger=MyLogger):
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

@inject
def main(logger=MyLogger):
    logger.debug("Sum program executed")
    logger.info(sum(2, 3))

if __name__ == "__main__":
    main()
{% endhighlight python %}

As we can see the readability of the code decrease because of the use of a isolated factory behind the *mylogger* function. Imagine a situation
where the factory decorated by the dependency maps is placed too far away, the code will become even harder to read than now. 

To try to figure out this problem, we will couple the configuration and the factory of create a new *Logger* instance into the *main* method. Luckly we have the
*register* method to inject the dependency programatically in execution time, it will help us to create the proper factory method being aware of the option
commands given by the user. The following code shows it:

{% highlight python %}
import sys
from functools import partial
from di import injector, Key, DependencyMap

from mylogging import Logger

dm = DependencyMap()
MyLogger = Key('logger')

inject = injector(dm)

@inject
def sum(x, y, logger=MyLogger):
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

@inject
def main(logger=MyLogger):
    logger.debug("Sum program executed")
    logger.info(sum(2, 3))

if __name__ == "__main__":
    try:
        debug = True if sys.argv[1] == '-v' else False
    except IndexError:
        debug = False

    logger_debug_aware = partial(Logger, debug=debug)
    dm.register(MyLogger, lambda _: logger_debug_aware(), flags=DependencyMap.SINGLETON | DependencyMap.FACTORY)
    main()
{% endhighlight python %}

We made it, although the readaballity of the code is still harder than the explcit dependency injection example.

## The global state symptom

Until now we hae seen how the DI libraries can decrese the readability of our code, even thought it gives us an automatically
way to inject the right instances into the functions as keyword args - [others](https://github.com/google/pinject) uses the arguments and a namming convention. But
from the beginning we have been stumbling with the issues regarding the [global state](http://programmers.stackexchange.com/questions/148108/why-is-global-state-so-evil).

The factory example that we used at the begging, where it printed twice the results of the program was affected by this problem. The following code shows the internals of the 
*mylogging* module. As you can see each time that the class is instanciated it registeres the *StreamHandler* handler, hereby as many instances of the *Logger* class
are created as many prints to the console will be done.

{% highlight python %}
import logging

class Logger(object):
    def __init__(self, debug=False):
        level = logging.INFO if not debug else logging.DEBUG
        self.__logger = logging.getLogger()
        self.__logger.addHandler(logging.StreamHandler())
        self.__logger.setLevel(level)

    def info(self, msg):
        self.__logger.info(msg)

    def debug(self, msg):
        self.__logger.debug(msg)
{% endhighlight python %}

Here the *root* logger is shared across of the all instances. When one of these instances modify the *root* logger the other ones are also affected by
the change. We could frame that as a *bugs from a mutable global state*. But the question here is ask to oursevles if the DI pattern overcomes the global
state problems: **Bugs from mutable global state, Poor testability, inflexibilty, code comphrension, concurreny issues, etc**.

As we saw before, the dependency injection pattern wires all of our functions with the same instance, either using a *singleton* pattern by the DI
library or passing the same instance to each function, worths to say that dependeny pattern derives in more flexibility and testability, event though we still
having a **global and share state*. Then We must be alert with the problems raised because of the mutable global state and concurreny issues.

Once we arrived here we might thing that the DI is not at all helping us to right better and safe code, even in case of the use of libraries that wire
the functions automatically **we are losing readebility**. Lets considerer the following apoximation of our *myloging* module:
a [global class](https://pythonconquerstheuniverse.wordpress.com/2010/10/20/a-globals-class-pattern-for-python/) pattern.

{% highlight python %}
import logging

class Logger(object):
    def __init__(self):
        self.__logger = logging.getLogger()
        self.__logger.addHandler(logging.StreamHandler())

    def level(self, debug=False)
        level = logging.INFO if not debug else logging.DEBUG
        self.__logger.setLevel(level)

    def info(self, msg):
        self.__logger.info(msg)

    def debug(self, msg):
        self.__logger.debug(msg)

logger = Logger()
{% endhighlight python %}

Here we faced the way of share the same instance along the code using a global class pattern. The code that uses this
module turns out being easy to read and mantain.

{% highlight python %}
import sys
from globallogging import logger

def sum(x, y):
    logger.debug("Sum {} and {}".format(x, y))
    return x + y

def main():
    logger.debug("Sum program executed")
    logger.info(sum(2, 3))

if __name__ == "__main__":
    try:
        debug = True if sys.argv[1] == '-v' else False
    except IndexError:
        debug = False
    logger.setup(debug)
    main()
{% endhighlight python %}

In contrast and because of the global state shared and mutability - the new *setup* method changes the behaviour of the logger class, and as
it is **we have increased the uncertainty of the program and its unflexibility, making almost impossible give different behaviours to different parts
of the code wihout affecting into each other**.

# Recaping

To sum up the following list tries to enumerate all of those things that we have seen in this post:

    * Dependency injection helps us to build code lossely coupled.
    * Consider the use of DI libraries taking into account the trade off between readability and functionality.
    * Global classes still have issues becuase of the global state nature, even thought they can be considered in scenarios where there is small chances of mutability.
