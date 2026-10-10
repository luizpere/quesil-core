from flask import Blueprint

portal_bp = Blueprint('portal', __name__, 
                      template_folder='templates',
                      static_folder='static')

from portal import routes
