from datetime import datetime

from entur_api import EnturGraphQL
from flask import Flask, request, jsonify

app = Flask(__name__)


class EnturJourneyPlannerV3(EnturGraphQL):
    endpoint = 'https://api.entur.io/journey-planner/v3/graphql'
    endpoint_folder = 'journey-planner'

    def departures(self, quay: str, line: str, limit=1):
        query = '''{
          quay(
            id: "%s"
          ) {
            id
            estimatedCalls(
              whiteListed: {
                lines: "%s"
              },
              numberOfDepartures: %d
            ) {
      expectedDepartureTime
      destinationDisplay {
        frontText
      }
      serviceJourney {
        publicCode
        journeyPattern {
          line {
            publicCode
          }
        }
      }
    }
    description
  }
}''' % (quay, line, limit)
        return self.run_query(query)


entur = EnturJourneyPlannerV3('datagutten-entur-python')


@app.route('/')
@app.route('/departures')
def departures():
    quay = request.args.get('quay')
    line = request.args.get('line')
    if not line and not quay:
        quay = 'NSR:Quay:11248'
        line = 'RUT:Line:66'
    result = entur.departures(quay, line, 5)
    return jsonify(result)


@app.route('/minutes')
def minutes():
    quay = request.args.get('quay')
    line = request.args.get('line')
    result = entur.departures(quay, line)
    departure = datetime.fromisoformat(result['data']['quay']['estimatedCalls'][0]['expectedDepartureTime'])
    now = datetime.now()
    now = now.astimezone(departure.tzinfo)
    diff = departure - now

    return str(int(diff.total_seconds() / 60))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
