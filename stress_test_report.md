# Stress Test

The tables cannot be seen corerctly in preview mode. Please read it not in preview mode

## 1

The first times trying the stress test with the locust tool the ml model crashed after a couple of seconds no matter the amount of users or the spawning rate. The same thing happened to other fellows. The error was about loading the image to the model. 

PIL.UnidentifiedImageError: cannot identify image file <_io.BytesIO object at 0x7f75f826ef40>

## 2

The first solution discussed in a support session was to save images with different names. This worked fine getting stable 9 RPS with 200 users but this way the utils.py didn't pass the code test and the stresst test generates hundreds of different images in a 1 minute test

Method	Name	    # Requests	# Fails	Average (ms)	Min (ms)	Max (ms)	Average size (bytes)	RPS	Failures/s
GET	    /	        232	        0	    17363	        897	        21204	    548	                    1.4	    0.0
POST	/predict	1165	    0	    18177	        889	        22351	    87	                    7.1	    0.0
Aggregated	        1397	    0	    18041	        889	        22351	    163	                    8.5	    0.0

### 3

After this I with the fellows decided tom implement a basic error handling with a try except in the ml_model. If the image cannot be processed it returns a 0 probaility and then the api detects it and returns a 400 http code. This way there is no need to save the image with different names and the utils.py script can pass the code test. This way it has a very similar performance with 200 users. The detail here is that errors start to appear but they are always around 1%

Method	Name	    # Requests	# Fails	Average (ms)	Min (ms)	Max (ms)	Average size (bytes)	RPS	Failures/s
GET	    /	        138	        0	    15295	        1098	    20749	    548                 	1.4	    0.0
POST	/predict	694	        13	    16185	        1077	    21828	    86                  	7.1	    0.1
Aggregated	        832	        13	    16037	        1077	    21828	    163	                    8.6	    0.1


### 4

Scalling the model image to have more than 1 container makes a big difference in performance. 

With 4 model conttainers it has this performance with 200 users. The RPS are considerably increased and also the response times are smaller. The con here is that the error rate increased to 7%

Method	Name	    # Requests	# Fails	Average (ms)	Min (ms)	Max (ms)	Average size (bytes)	RPS	Failures/s
GET	    /	        600	        0	    4577	        2	        5958	    548                 	3.8	    0.0
POST	/predict	3139	    246	    4945	        67	        6498	    85	                    19.8	1.5
Aggregated	        3739	    246	    4886	        2	        6498	    159	                    23.5	1.5

The maximum amount of users that the api can process running in my laptopt is around 600. Beyomd this number it becomes unstable with error rate of 50%. With 600 users and 4 model containers the error rate is 6%

Method	Name	    # Requests	# Fails	Average (ms)	Min (ms)	Max (ms)	Average size (bytes)	RPS	Failures/s
GET	    /	        628	        0	    15930	        3	        22818	    548	                    3.7	    0.0
POST	/predict	3317	    246	    16745	        62	        23252	    85	                    19.7	1.5
Aggregated	        3945	    246	    16615	        3	        23252	    158	                    23.4	1.5

