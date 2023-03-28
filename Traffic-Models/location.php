
<?php
  // Define the API endpoint for traffic data
  $url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=30.759272%2C76.775724&destinations=30.759974%2C76.791659&mode=driving&departure_time=now&traffic_model=best_guess&key=AIzaSyBbv3OuDF33wd81JY8ecGPFNevmWXmpFpA&alternatives=true";

  // Make a request to the API endpoint
  $response = file_get_contents($url);

  // Decode the JSON response
  $data = json_decode($response, true);

  // Get the traffic congestion status
  $status = $data['rows'][0]['elements'][0]['status'];

  // Check the status and display the traffic congestion status
  if ($status == "OK") {
	var_dump($data['rows'][0]['elements']);
    $congestion = $data['rows'][0]['elements'][0]['duration_in_traffic']['text'];
    echo "Traffic congestion: $congestion";
  } else {
    echo "Error: Traffic information is not available for this location.";
  }



  
  $url2= "https://api.openweathermap.org/data/2.5/weather?lat=30.763106&lon=76.783702&appid=ab6c03ba81aff0f9c72151d5f4dbcdd7";

  // Make a request to the API endpoint
  $response2 = file_get_contents($url2);

  // Decode the JSON response
  $data2 = json_decode($response2, true);

  // Get the traffic congestion status
  var_dump($data2);


?>



<html>
<head>
  <style>
    /* Set the height of the map */
    #map {
      height: 600px;
      width: 100%;
    }
	.info{
		height: 100px;
	}
	.info-div{
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100px;
	}
  </style>
</head>
<body>
  <div id="map"></div>

  <script>
  var temperature=0;
    function initMap() {


      var start = {lat: 30.759272, lng: 76.775724};
      var end = {lat: 30.759974, lng: 76.791659};
	  var location1 = new google.maps.LatLng(30.759272, 76.775724);
	  var location2 = new google.maps.LatLng(30.759974, 76.791659);
	  var midpoint = google.maps.geometry.spherical.interpolate(location1, location2, 0.5);
      var directionsService = new google.maps.DirectionsService();
      var directionsDisplay = new google.maps.DirectionsRenderer({
		//suppressMarkers: true
		});


      var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13,
        center: start
      });



	  var infowindow;
      directionsDisplay.setMap(map);
      directionsService.route({
        origin: start,
        destination: end,
		provideRouteAlternatives: false,
        travelMode: 'DRIVING',
		drivingOptions: {
              departureTime: new Date(),
              trafficModel: "bestguess"
            }
      }, function(response, status) {
        if (status === 'OK') {
          directionsDisplay.setDirections(response);
        } else {
          window.alert('Directions request failed due to ' + status);
        }
      });



	  var trafficLayer = new google.maps.TrafficLayer();
      trafficLayer.setMap(map);
	  var image='https://cdn.pixabay.com/photo/2016/06/26/23/32/information-1481584_960_720.png';
	  var size = new google.maps.Size(64, 64);
	  var marker = new google.maps.Marker({
        map: map,
        position: midpoint,
		icon:{
			url:image,
			scaledSize: size
		}
      });



	  infowindow = new google.maps.InfoWindow();
      updateWeather(infowindow,map,marker);
	  marker.addListener('click', function() {
		  infowindow.open(map, marker);
		});
    }


  </script>



  <script>
	function updateWeather(infowindow,map,marker) {
      function roundToTwo(num) {
		  return Math.round(num * 100) / 100;
		}


	  var xhr = new XMLHttpRequest();
      xhr.open('GET', 'https://api.openweathermap.org/data/2.5/weather?lat=30.763106&lon=76.783702&appid=ab6c03ba81aff0f9c72151d5f4dbcdd7', true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          temperature = roundToTwo(data.main.temp - 273.15);
          var weather = data.weather[0].main;

          infowindow.setContent('<div class="info-div"><img src="https://cdn.pixabay.com/photo/2013/04/01/08/38/satellite-98427_960_720.png" class="info"></div><hr/><strong>Temperature:</strong> ' + temperature + '°C' + '<br>' + '<strong>Weather: ' + weather);
          infowindow.open(map, marker);
        }
      };
      xhr.send();
    }
  </script>



  <script src="https://maps.googleapis.com/maps/api/js?libraries=geometry&key=AIzaSyBbv3OuDF33wd81JY8ecGPFNevmWXmpFpA&callback=initMap">
  </script>
  <script>
    window.onload = function() {
      // Your code here
      
    };
  </script>
</body>
</html>
