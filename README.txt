==========================
 Data packaging utilities
==========================

The utilities form a shell in which you can link actual data.

We avoid keeping the data in this shell because of the overheads for the
repository.

For example, if your current directory is the root directory of these
utilities (containing this README file), then you might do something
like::

   ln -s /location/of/example_data nipy-data/data
   ln -s /location/of/template_data nipy-templates/templates

Here ``/location/of/example_data`` would be a directory containing the
``config.ini`` file and the directory and files that will be exported by
the ``nipy-data`` package.

We've set ``svn:ignore`` to ignore directories ``nipy-data/data`` and
``nipy-templates/templates`` to keep the actual data out of the
repository for now.  We can revisit if that becomes a problem.

Once you have done this::

   make templates
   make data

and then::

   make publish_templates
   make publish_data


