angular.module('app', [
   'ngStorage',
   'ngRoute',
   'angular-loading-bar'
])
.constant('urls', {
   BASE: '',
   BASE_API: '/api/v1'
})
.config(['$routeProvider', '$httpProvider', function ($routeProvider, $httpProvider) {
        $routeProvider.
            when('/', {
                templateUrl: '/static/views/home.tpl.html',
                controller: 'HomeController'
            }).
            when('/signin', {
                templateUrl: '/static/views/signin.tpl.html',
                controller: 'HomeController'
            }).
            when('/signup', {
                templateUrl: '/static/views/signup.tpl.html',
                controller: 'HomeController'
            }).
            when('/change_password', {
                templateUrl: '/static/views/change.password.tpl.html',
                controller: 'HomeController'
            }).
            when('/hidden_area', {
                templateUrl: '/static/views/hidden.area.tpl.html',
                controller: 'HiddenDataController'
            }).
            otherwise({
                redirectTo: '/'
            });
        $httpProvider.interceptors.push(['$q', '$location', '$localStorage', function ($q, $location, $localStorage) {
           return {
               'request': function (config) {
                   config.headers = config.headers || {};
                   if ($localStorage.token) {
                       config.headers.Authorization = 'Bearer ' + $localStorage.token;
                   }
                   return config;
               },
               'responseError': function (response) {
                   if (response.status === 401 || response.status === 403) {
                       $location.path('/signin');
                   }
                   return $q.reject(response);
               }
           };
}]);}]);


