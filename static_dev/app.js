
  <script type="text/javascript" src="static>
    function startServiceWait() {
    }

    function endServiceWait() {
    }

    function showServiceError(error) {
      if (error.responseText) {
        console.log(error.responseText);
      }
    }

    function invokeService(method, path, data, onSuccess) {
      startServiceWait();
      $.ajax({
        type: method,
        url: "/api/1.0/" + path,
        data: data,
        contentType: "application/json",
        headers: { "x-api-key": $("#apiKeyInput").val() }
      })
      .done(onSuccess)
      .fail(showServiceError)
      .always(endServiceWait);
    }

    /*********/

    function refreshBoxList() {
      invokeService("GET", "boxx/", {}, function(results) {
        $("#dependsOnApiKey").show()
        $("#listOfBoxes").empty();
        if (!results.data || !!results.data.length) {
          $("#listOfBoxes").append($("<span style='color: orange'>None</span>"));
        }
        else {
          for (var i = 0, len = results.data.length; i < len; ++i) {
            $("#listOfBoxes").append($("<li onclick=>" + results.data[i].name + "</li>"));
          }
        }
      });
    }

    function addClicked() {
      $("#dependsOnNewBox").show();
      $("#dependsOnSelectedBox").hide();
      $("#dependsOnValidatedBox").hide();
      $("#boxDefinitionInput").val($("#sampleBoxDefinitionInput").val())
    }

    function boxSelected(id) {
      selectedBoxId = id;
      invokeService("GET", "boxx/" + id, {}, function(results) {
        renderBoxDefIntoTable(results.data, "selectedBoxDefTable");
      });
    }

    function renderBoxDefIntoTable(data, tableId) {
      $("#" + tableId).replaceWith(renderBoxDef(data).attr("id", tableId));
    }

    function validateClicked() {
      invokeService("POST", "boxx/validate", $("#boxDefinitionInput").val(), function(results) {
        renderBoxDefIntoTable(results.data, "validatedBoxDefTable")
        $("#dependsOnNewBox").hide();
        $("#dependsOnSelectedBox").hide();
        $("#dependsOnValidatedBox").show();
      });
    }

    function saveClicked() {
      invokeService("POST", "boxx", $("#boxDefinitionInput").val(), function(results) {
        refreshBoxList();
        $("#dependsOnNewBox").hide();
        $("#dependsOnSelectedBox").hide();
        $("#dependsOnValidatedBox").hide();
      });
    }

    function renderBoxDef(boxdef) {
      var table = $("<table>")
      function renderRow(label, value) {
        table.append($("<tr>").append($("<td>").append($("<b>").text(label))).append($("<td>").append($("<span>").text(value))))
      }
      renderRow("Title", boxdef.title)
      renderRow("Description", boxdef.description)
      renderRow("Size", boxdef.size)
      renderRow("Amount In", boxdef.amount_in)
      renderRow("Hit Rate", boxdef.hit_rate)
      renderRow("Average Return", boxdef.average_return)
      for (var i = 0, len = boxdef.outcomes.length; i < len; ++i) {
        var prefix = "Outcome #" + (i + 1) + " ";
        renderRow(prefix + "Title", boxdef.outcomes[i].title)
        renderRow(prefix + "Description", boxdef.outcomes[i].description)
        renderRow(prefix + "Probability", boxdef.outcomes[i].probability)
        renderRow(prefix + "Amount Out", boxdef.outcomes[i].amount_out)
        renderRow(prefix + "Hit Rate", boxdef.outcomes[i].hit_rate)
        renderRow(prefix + "Average Return", boxdef.outcomes[i].average_return)
      }
      return table
    }

    /*********/

    $(document).ready(function() {
      $("#apiKeyInput").val("$$$$$$$$.TESTER.$$$$$$$$");
      apiKeyChanged();
    });
