from django.http import HttpResponse

import unicodecsv as csv


def render_to_response_as_csv(request, report, filename=None, context=None):
  """
    Generates a CSV file as a response from the report dict.

    Params:
        report:  is a dict of the following format
            {
                "pre_headers": [],
                "headers": [],
                "rows": [],
            }

    """
  if not filename:
    filename = "export.csv"
  if context is None:
    context = {}

  response = HttpResponse(content_type="text/csv")
  writer = csv.writer(response)
  for row in report.get("pre_headers", []):
    writer.writerow(row)
  writer.writerow(report["headers"])
  for row in report["rows"]:
    writer.writerow(row)

  response["Content-Disposition"] = ("attachment;" "filename={0}".format(filename))
  return response
