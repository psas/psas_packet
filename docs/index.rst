PSAS Packet Serializer
======================

.. sidebar:: Contents

    .. toctree::
       :maxdepth: 2

       packet
       api
       network
       examples

`Portland State Aerospace Society <http://psas.pdx.edu/>`_  (PSAS) is a student
aerospace engineering project at Portland State University. We are building
ultra-low-cost, open source rockets that feature some of the most sophisticated
amateur rocket avionics systems out there today.

In developing our `telemetry <https://github.com/psas/telemetry>`_ system we've
had to come up with a tight data storage and transfer technique. However we use
this data scheme in many different projects, from the flight computer to 
various ground stations. This project is developed to have a single place that
defines everything.

psas_packet
-----------

psas_packet is the reference implementation of our binary message storage and
transmission scheme.
