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

  function printHash(hash) {
  }

  function cleanErrorText(errorText) {
    var obj;
    try {
      obj = JSON.parse(errorText);
    }
    catch (e) {
      return errorText;
    }
    if (obj.message) {
      errorText = obj.message;
    }
    else if (obj.detail) {
      errorText = obj.detail;
    }
    if (obj.errors) {
      var parts = [];
      for (var i = 0, len = obj.errors.length; i < len; ++i) {
        var errhash = obj.errors[i];
        if (errhash) {
          for (var key in errhash) {
            parts.push(key + ": " + errhash[key]);
          }
        }
      }
      errorText += " " + parts.join(", ") + ".";
    }
    return errorText;
  }

  function handleServiceError(jqXHR, textStatus, errorThrown) {
    var errorText = cleanErrorText(jqXHR.responseText);
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
    .always(endServiceWait)
    .fail(handleServiceError);
    if (onError) {
      promise.fail(onError);
    }
  }

  function invokeJsonService(method, path, data, onSuccess, onError) {
    invokeService(method, path, JSON.stringify(data), onSuccess, onError);
  }

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
  var apiKeyListeners = [];

  function refreshApiKey() {
    var apiKey = apiKeyCookie.get();
    if (apiKey) {
      $(".apiKeyPrompt").hide();
      $(".apiKeyWidget")
        .empty()
        .append($("<span class='infoLabel'>").text("Using API key: "))
        .append($("<span class='infoValue'>").text(apiKeyCookie.get()))
        .append($("<span>").text(" "))
        .append($("<button>").text("Clear").click(clearApiKey));
    }
    else {
      $(".apiKeyPrompt").show();
      $(".apiKeyWidget")
        .empty()
        .append($("<input class='infoInput'; placeholder='API key'>"))
        .append($("<button>").text("Enter").click(enterApiKey));
    }
    for (var i = 0, len = apiKeyListeners.length; i < len; ++i) {
      apiKeyListeners[i]({ apiKey: apiKey });
    }
  }

  function enterApiKey() {
    var newApiKey = $(this).parent().find("input").val();
    apiKeyCookie.set(newApiKey);
    Service.invoke("GET", "boxx", {}, refreshApiKey, clearApiKey);
  }

  function clearApiKey() {
    apiKeyCookie.clear()
    refreshApiKey();
  }

  $(document).ready(refreshApiKey);

  function addApiKeyListener(listener) {
    apiKeyListeners.push(listener);
  }

  g.Service = {
    invoke: invokeService,
    invokeJson: invokeJsonService,
    addApiKeyListener: addApiKeyListener
  };

})(window, document, jQuery);
