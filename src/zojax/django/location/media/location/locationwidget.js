(function() {
	
	PRECISION_PRIORITY = [
      'street_address',
      'sublocality',	                      
      'locality',
	  'administrative_area_level_3',
	  'administrative_area_level_2',
	  'administrative_area_level_1',
	  'country'
    ];
	
	/*config is of the form
    {canvas: "some-dom-element-id",
     lat_field: "some-dom-element-id",
     lng_field: "some-dom-element-id",
     country_field: "some-dom-element-id",
     state_field: "some-dom-element-id",
     city_field: "some-dom-element-id",
     search_field: "some-dom-element-id",
     search_button: "some-dom-element-id", 
     precision: "locality"
    */
	
	window.LocationWidget = function(config) {
	    config =  $.extend({readonly: false, 
                            precision: 'locality',
                            showMap: true},
                            config);
	    this.$canvas = $(config.canvas);
		this.$lat_field = $(config.lat_field);
		this.$lng_field = $(config.lng_field);
		this.$country_field = $(config.country_field);
		this.$state_field = $(config.state_field);
		this.$city_field= $(config.city_field);
		this.$search_field = $(config.search_field);
		this.$search_button = $(config.search_button);
		this.precision = config.precision;
		this.init();
	}
	
	LocationWidget.prototype = {
		init: function() {
			var self = this;
			var lat = this.$lat_field.val();
			var lng = this.$lng_field.val();
			var initial_location = null;
			if (lat != '' && lng != '') {
				initial_location = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
			}
			this.geocoder = new google.maps.Geocoder();
			if (initial_location == null) {
			 	initial_location = new google.maps.LatLng(40.69847032728747, -73.9514422416687); // New York
//				if (navigator.geolocation) {
//				 	navigator.geolocation.getCurrentPosition(
//			 			function(position) {
//					 		initial_location = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
//					 	    self.map.setCenter(initial_location);
//					 	    self.setMarker(initial_location);
//				 	    },
//				 	    function() {return;}
//				 	);
//				}
			} 
			var map_options = {
					zoom: 8,
					center: initial_location,
					mapTypeId: google.maps.MapTypeId.ROADMAP
			    };
			this.map = new google.maps.Map(this.$canvas.get(0), map_options);
		    this.marker = new google.maps.Marker({
		        map: this.map, 
		        position: initial_location
		    });
		    this.setMarker(initial_location);
		    this.info_window = new google.maps.InfoWindow();
		    google.maps.event.addListener(this.map, 'click', function(event) {
		        self.setMarker(event.latLng);
		    });
		    this.$search_button.click(function() {self.search();});
		    this.$search_field.keydown(function(event) {
		    	if (event.keyCode == '13') {
		    		self.search();
		    	    event.preventDefault();
		        }
	    	});
		},
		
		getComponent: function getComponent(resp, type, format) {
		    if (!format)
		        format='long_name';
		        
            for (var i = 0; i < resp.length; i++) {
                for (var k = 0; k < resp[i].types.length; k++) {
                    if (type == resp[i].types[k])
                        return resp[i][format]
                }
            }
        },
		
		setMarker: function(location) {
			this.marker.setPosition(location);
			this.$lat_field.val(location.lat());
			this.$lng_field.val(location.lng());
			var self = this;
			this.geocoder.geocode({'latLng': location}, function(results, status) {
				var address = null;
				if (status == google.maps.GeocoderStatus.OK) {
					if (results.length) {
						for (var i = PRECISION_PRIORITY.indexOf(self.precision); i < PRECISION_PRIORITY.length; i++) {
							var precision = PRECISION_PRIORITY[i]; 
							for (var j = 0; j < results.length; j++) {
								var result = results[j];
								if (result.types.indexOf(precision) != -1) {
									address = result.formatted_address;
									break;
								}
							}
							if (address != null) {
								break;
							}
							if (address == null) {
								address = results[0].formatted_address;
							}
						}
						var resp = results[0].address_components;
						self.$country_field.val(self.getComponent(resp, 'country'));
						self.$state_field.val(self.getComponent(resp, 'administrative_area_level_1'));
						self.$city_field.val(self.getComponent(resp, 'locality'));
					}
					if (address != null) {
						self.info_window.setContent(address);
						self.info_window.open(self.map, self.marker);
					} else {
						self.info_window.close();
					}
				} else {
					alert("Geocoder failed due to: " + status);
				}
			});
		},
		
		search: function() {
			var address = this.$search_field.val();
			if (address == '') {
				return;
			}
			var self = this;
			this.geocoder.geocode({'address': address}, function(results, status) {
				if (status == google.maps.GeocoderStatus.OK) {
					if (results.length) {
						self.setMarker(results[0].geometry.location);
					}
				} else {
					alert("Geocoder failed due to: " + status);
				}
			});
		}
	};
})();