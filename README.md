# Lenovo PSREF Database Generator

This project is a Python script that generates a SQLITE database of Lenovo PSREF (Product Specifications Reference) data.

Currently, it scrapes all currently available (not withdrawn) laptops from the PSREF website and creates a Sqlite database containing the specifications of these laptops.

This will be used to create a web application that allows users to search for Lenovo laptops in detail. Most websites do not allow such a granular search. Especially not for the entire range of laptops that Lenovo offers.

I will have to set up a cron job to make sure that the database is updated regularly, as Lenovo updates their PSREF data frequently. This could get expensive. But this is just to explore the feasibility of such a project.
