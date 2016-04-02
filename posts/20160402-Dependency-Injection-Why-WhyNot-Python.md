# Dependency Injection, why and wny not hate it using Python

Recently the DI pattern has appeard in front of me as a new design pattern, no matters how but it
challenged me. I wasnt keen on design patterns as a programmer, not beause I thing this is not
a iteresting field, I guess the subject by it self it have never caught me instead of other fields.

My small knowledge about design patters is due to those friends that I have the opportunity to work with them, and
sometimes their teaching has challenged me to improve in some are regarding the design patterns.

There are a lot of literature about DI and IoC over there, from this [post](//martinfowler.com/articles/injection.html) 
by Martin Flowers till good [threads](//stackoverflow.com/questions/130794/what-is-dependency-injection) in stackoverflow,
but Im keen on move this conversation in the Python context where this pattern is not  used by the most of projects and community.

The following snippet shows the code that I used to challenge me, it uses a [DI library[(//stackoverflow.com/questions/130794/what-is-dependency-injection) 
that takes benefeit of the Python by it self to help the developer to inject thoses dependencies over functions or clasess using
decorators, metaclasses or protocol descriptors.

        import di
        
        if __name__ == "__main"
