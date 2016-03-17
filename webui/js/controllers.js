angular.module('app')
   .controller('HomeController', ['$rootScope', '$scope', '$location', '$localStorage', 'Auth',
       function ($rootScope, $scope, $location, $localStorage, Auth) {
           function successAuth(res) {
               $localStorage.token = res.token;
               $location.path("/");
           }


           $scope.signin = function () {
               var formData = {
                   email: $scope.email,
                   password: $scope.password
               };

               Auth.signin(formData, successAuth, function () {
                   $rootScope.error = 'Invalid credentials.';
               })
           };

           $scope.changePassword = function () {
               var formData = {
                   old_password: $scope.oldPassword,
                   new_password: $scope.newPassword,
                   new_password_confirm: $scope.newPasswordConfirm
               };
                Auth.changePassword(formData, function(){
                    $location.path("/");
                }, function (){
                    $rootScope.error = 'Failed to change password';
                })
           };

           $scope.signup = function () {
               var formData = {
                   email: $scope.email,
                   password: $scope.password
               };

               Auth.signup(formData,
                   function() {
                       // Signup done
                   }, function () {
                       $rootScope.error = 'Failed to signup';
                   })
           };

           $scope.logout = function () {
               Auth.logout(function () {
                   $location.path("/");
               });
           };
           $scope.token = $localStorage.token;
           $scope.tokenClaims = Auth.getTokenClaims();
       }])
    .controller('HiddenDataController', ['$rootScope', '$scope', 'HiddenData', function ($rootScope, $scope, HiddenData) {
           HiddenData.getProtectedMessage({}, function(res){
               $scope.secretText = res.message;
           }, function () {
               $rootScope.error = 'Failed to fetch restricted content.';
           });

       }]);