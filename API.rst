API
===

API is built using `Django REST Faramework <http://django-rest-framework.org/`_.
Flllowing is a list of available API calls with short description. API calls that
expected to return single object instance return HTTP status 404 if object cannot
be found. All API calls that return some content use JSON-encoding.


GET /api/client/:client_slug
----------------------------

Retrieve client object matching ``client_slug``.


GET /api/client/:client_slug/summary
------------------------------------

Retrieve client summary consisting of following named values:

	``totat_customers``
		Number of customers in database
	
	``redeemers``
		Number of customers that redeemed coupon
	
	``new_signups``
		Number of new customers


GET /api/client/:client_slug/customer_fields
--------------------------------------------

Retrieve customer fields information for the client as a object/hash with the following fields:

	``available_customer_fields``
		Unordered list of customer field **objects**
	``display_customer_fields``
		Ordered list of customer field **names**

Each customer field object consists of the following fields:

        ``name``
                Short field name

        ``title``
                Field description suitable as form input labels or table column captions

        ``type``
                Field type

        ``required``
                Whether or not this field is mandatory for every customer of this client


PUT /api/client/:client_slug/customer_fields
--------------------------------------------

Update customer fields to display on customer list. Request JSON-encoded body should have
the following parameters:

        ``display_customer_fields``
                List of customer field **names**

Response is JSON-encoded objec/hash and includes the following fields:

        ``display_customers_fields``
                List of customer field **names** as it's been saved on server.
                
                **Note** This can be different from what was in request due to filtering
                and other reasons.


GET /api/client/:client_slug/customers
--------------------------------------

Retrieve list of client's customers. Each customer object consists of the following fields:

	``id``
		Customer ID
	``data``
		Object with dynamic set of fields. Its content depends on what is stored in
		database but can be restricted by ``fields`` qery string parameter

The following query string parameters can be used to contol result:

	``offset``
		Skip first ``offset`` number of customers. If omitted no customers skipped

	``limit``
		Limit number of returend customers to ``limit``. If omitted no limit is set
	
	``fields``
		Comma-separated list of field names to include into data field. Must be a
		subset of client's customer fields set. If not specified all fields will be included
		in response. Example:

			GET /api/client/abc/customers?fields=email,first_name,last_name,dob,phone
	
	``order``
		Ordered list of comma-separated field names. Controls sorting order of customer objects.
		If name is prefixed with "-" descending order on that field is used. If not specified
		order is not determined. Example:

			GET /api/client/abc/customers?order=-dob,last_name

	``search``
		Do full-text search across customer list. Example:

                        GET /api/client/abc/customers?search=John+Doe

Any combination of qury string parameters is allowed as long as there is only one of each parameter.
``limit`` and ``offset`` parameters are applied after ``search`` and ``order``, that's it customers
are filtered by search criteria, then sorted according to ``order`` then ``offset`` and ``limit`` applied
on resulting list.
