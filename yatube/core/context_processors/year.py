from datetime import datetime


def year(request):
    dt_year = datetime.now().year
    return {
        'year': dt_year
    }
