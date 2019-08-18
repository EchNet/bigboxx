from dateutil.relativedelta import relativedelta
from .cycle import start_of_day


def daterange(start_date, end_date, include_end=False):
  """
    Generator to iterate over a range of dates.
    """
  if include_end:
    end_date = end_date + relativedelta(days=1)
  for n in range(int((end_date - start_date).days)):
    yield start_date + relativedelta(days=n)


def slice_time_range(time_slice, first_date, last_date):
  #
  # Given a date range and a unit of time, this function slices the range, creating an array
  # of dictionaries containing start_date, end_date, and label.
  #

  def slice_by_day(start_date):
    return {
        "start_date": start_date,
        "end_date": start_date + relativedelta(days=1),
        "label": start_date.strftime("%Y-%m-%d")
    }

  def slice_by_month(start_date):
    return {
        "start_date": start_date,
        "end_date": start_date.replace(day=1) + relativedelta(months=1),
        "label": start_date.strftime("%Y-%m")
    }

  def slice_by_quarter(start_date):
    quarter = ((start_date.month - 1) // 3) + 1
    qmonth = (((start_date.month - 1) // 3) * 3) + 1
    return {
        "start_date": start_date,
        "end_date": start_date.replace(day=1, month=qmonth) + relativedelta(months=3),
        "label": "Q%d %d" % (quarter, start_date.year)
    }

  def slice_by_year(start_date):
    return {
        "start_date": start_date,
        "end_date": start_date.replace(day=1, month=1) + relativedelta(years=1),
        "label": start_date.strftime("%Y")
    }

  def decorate_slice(slice):
    slice["start_time"] = start_of_day(slice.get("start_date"))
    slice["end_time"] = start_of_day(slice.get("end_date"))
    return slice

  slices = []
  slicer = locals()["slice_by_%s" % time_slice]
  slice = slicer(first_date)
  final_end_date = last_date + relativedelta(days=1)
  while slice.get("end_date") < final_end_date:
    slices.append(decorate_slice(slice))
    slice = slicer(slice.get("end_date"))
  slice["end_date"] = final_end_date
  slices.append(decorate_slice(slice))
  return slices
