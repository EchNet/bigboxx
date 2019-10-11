(function(g, document, $) {

  /******* Services *******/

  var errorTextReplacements = [
    [ "Authentication credentials were not provided", "Invalid API key." ]
  ]

  function startServiceWait() {
    $("body").addClass("wait")
    $(".serviceErrorContainer").hide();
  }

  function endServiceWait() {
    $("body").removeClass("wait")
  }

  function handleServiceError(jqXHR, textStatus, errorThrown) {
    var errorText = jqXHR.responseText || "Error!";
    for (var i = 0, len = errorTextReplacements.length; i < len; ++i) {
      if (errorText.indexOf(errorTextReplacements[0][0]) >= 0) {
        errorText = errorTextReplacements[0][1];
      }
    }
    console.log(errorText);
    $(".serviceErrorText").text(errorText);
    $(".serviceErrorContainer").show();
  }

  function invokeService(method, path, data, onSuccess, onError) {
    startServiceWait();
    promise = $.ajax({
      type: method,
      url: "/api/1.0/" + path,
      data: data,
      contentType: "application/json",
      headers: { "x-api-key": apiKeyCookie.get() }
    })
    .done(onSuccess)
    .always(endServiceWait);
    if (onError) {
      promise = promise.fail(onError);
    }
    promise.fail(handleServiceError);
  }

  function invokeJsonService(method, path, data, onSuccess, onError) {
    invokeService(method, path, JSON.stringify(data), onSuccess, onError);
  }

  function replaceErrorText(regex, replacementText) {
    errorTextReplacements.append([ regex, replacementText ])
  }

  g.Service = {
    invoke: invokeService,
    invokeJson: invokeJsonService,
    replaceErrorText: replaceErrorText,
  };

  /******* Cookies *******/

  function Cookie(name) {
    this.name = name;
  }

  Cookie.prototype = {
    get: function() {
      var name = this.name;
      var value = "; " + document.cookie;
      var parts = value.split("; " + name + "=");
      if (parts.length == 2) return parts.pop().split(";").shift();
    },
    set: function(value) {
      var name = this.name;
      document.cookie = name + "=" + value + "; Path=/; Expires=Thu, 01 Jan 2100 00:00:01 GMT;";
    },
    clear: function() {
      var name = this.name;
      document.cookie = name + "=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;";
    }
  }

  /******* API key widget *******/

  var apiKeyCookie = new Cookie("bigboxx-api-key");

  function refreshApiKeyWidget() {
    if (apiKeyCookie.get()) {
      $(".apiKeyPrompt").hide();
      $(".apiKeyWidget")
        .empty()
        .append($("<span class='infoLabel'>").text("Using API key: "))
        .append($("<span class='infoValue'>").text(apiKeyCookie.get()))
        .append($("<span>").text(" "))
        .append($("<button>").text("Clear").click(clearApiKey));
    }
    else {
      $(".apiKeyPrompt").hide();
      $(".apiKeyWidget")
        .empty()
        .append($("<input class='infoInput'; placeholder='API key'>"))
        .append($("<button>").text("Enter").click(enterApiKey));
    }
  }

  function enterApiKey() {
    apiKeyCookie.set($(this).parent().find("input").val());
    Service.invoke("GET", "boxx", {}, function() {
      refreshApiKeyWidget()
    }, function() {
      apiKeyCookie.clear();
      refreshApiKeyWidget()
    });
  }

  function clearApiKey() {
    apiKeyCookie.clear()
    refreshApiKeyWidget()
  }

  $(document).ready(refreshApiKeyWidget)

  g.apiKeyCookie = apiKeyCookie;

})(window, document, jQuery);
