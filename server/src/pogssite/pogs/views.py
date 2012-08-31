from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader
from config import django_image_dir
from image import fitsimage
from sqlalchemy.orm import sessionmaker
from django.db import connection
from pogs.models import Galaxy
from pogs import PogsSession
from database import database_support
import os, io, datetime, tempfile

class GalaxyLine:
    name1 = ""
    name2 = ""
    name3 = ""
    name4 = ""
    name5 = ""
    name6 = ""
    id1 = ""
    id2 = ""
    id3 = ""
    id4 = ""
    id5 = ""
    id6 = ""
    redshift1 = ""
    redshift2 = ""
    redshift3 = ""
    redshift4 = ""
    redshift5 = ""
    redshift6 = ""
    width1 = 100
    width2 = 100
    width3 = 100
    width4 = 100
    width5 = 100
    width6 = 100
    height1 = 100
    height2 = 100
    height3 = 100
    height4 = 100
    height5 = 100
    height6 = 100
    
def getReferer(request):
    try:
        referer = request.META['HTTP_REFERER']
    except KeyError as e:
        referer = None
        
    if referer == '' or referer == None:
        referer = 'pogs'
    else:
        parts = referer.split('/')
        referer = parts[3]
    if referer == 'pogssite':
        referer = getRefererFromCookie(request)
    request.COOKIES['pogs_referer'] = referer
    return referer

def getRefererFromCookie(request):
    try:
        referer = request.COOKIES['pogs_referer']
    except KeyError as e:
        referer = None
    if referer == '' or referer == None:
        referer = 'pogs'
    return referer;

def userGalaxies(request, userid):
    session = PogsSession()
    image = fitsimage.FitsImage()

    user_galaxy_list = []
    idx = 0
    galaxy_line = GalaxyLine()
    for galaxy in image.userGalaxies(session, userid):
        name = galaxy.name
        if galaxy.version_number > 1:
            name = galaxy.name + "[" + str(galaxy.version_number) + "]"
        if idx == 0:
            galaxy_line = GalaxyLine()
            galaxy_line.name1 = name
            galaxy_line.id1 = galaxy.galaxy_id
            galaxy_line.redshift1 = str(galaxy.redshift)
            user_galaxy_list.append(galaxy_line)
            idx = 1
        elif idx == 1:
            galaxy_line.name2 = name
            galaxy_line.id2 = galaxy.galaxy_id
            galaxy_line.redshift2 = str(galaxy.redshift)
            idx = 2
        elif idx == 2:
            galaxy_line.name3 = name
            galaxy_line.id3 = galaxy.galaxy_id
            galaxy_line.redshift3 = str(galaxy.redshift)
            idx = 3
        elif idx == 3:
            galaxy_line.name4 = name
            galaxy_line.id4 = galaxy.galaxy_id
            galaxy_line.redshift4 = str(galaxy.redshift)
            idx = 4
        elif idx == 4:
            galaxy_line.name5 = name
            galaxy_line.id5 = galaxy.galaxy_id
            galaxy_line.redshift5 = str(galaxy.redshift)
            idx = 5
        elif idx == 5:
            galaxy_line.name6 = name
            galaxy_line.id6 = galaxy.galaxy_id
            galaxy_line.redshift6 = str(galaxy.redshift)
            idx = 0
    session.close()
    referer = getReferer(request)

    t = loader.get_template('pogs/index.html')
    c = Context({
        'user_galaxy_list': user_galaxy_list,
        'userid':           userid,
        'referer':          referer,
    })
    return HttpResponse(t.render(c))

def userGalaxy(request, userid, galaxy_id):
    session = PogsSession()
    userid = int(userid)
    galaxy_id = int(galaxy_id)
    galaxy = session.query(database_support.Galaxy).filter("galaxy_id=:galaxy_id").params(galaxy_id=galaxy_id).first()
    galaxy_name = galaxy.name
    if galaxy.version_number > 1:
        galaxy_name = galaxy.name + "[" + str(galaxy.version_number) + "]"
    galaxy_height = galaxy.dimension_x;
    galaxy_width = galaxy.dimension_y;
    session.close()
    
    referer = getRefererFromCookie(request)
    
    t = loader.get_template('pogs/user_images.html')
    c = Context({
        'userid': userid,
        'galaxy_id': galaxy_id,
        'galaxy_name': galaxy_name,
        'galaxy_width': galaxy_width,
        'galaxy_height': galaxy_height,
        'referer':          referer,
    })
    return HttpResponse(t.render(c))

def userGalaxyImage(request, userid, galaxy_id, colour):
    tmp = tempfile.mkstemp(".png", "pogs", None, False)
    file = tmp[0]
    os.close(file)

    imageDirName = django_image_dir

    outImageFileName = tmp[1]

    session = PogsSession()
    userid = int(userid)
    galaxy_id = int(galaxy_id)
    galaxy = session.query(database_support.Galaxy).filter("galaxy_id=:galaxy_id").params(galaxy_id=galaxy_id).first()
    imagePrefixName = galaxy.name + "_" + str(galaxy.version_number)

    image = fitsimage.FitsImage()
    inImageFileName = image.get_colour_image_path(imageDirName, imagePrefixName, colour, False)
    image.markImage(session, inImageFileName, outImageFileName, galaxy_id, userid)
    session.close()

    sizeBytes = os.path.getsize(outImageFileName)
    file = open(outImageFileName, "rb")
    myImage = file.read(sizeBytes)
    file.close()
    os.remove(outImageFileName)

    DELTA = datetime.timedelta(minutes=10)
    DELTA_SECONDS = DELTA.days * 86400 + DELTA.seconds
    EXPIRATION_MASK = "%a, %d %b %Y %H:%M:%S %Z"
    expires = (datetime.datetime.now()+DELTA).strftime(EXPIRATION_MASK)

    response = HttpResponse(myImage, content_type='image/png')
    response['Content-Disposition'] = 'filename=\"' + imagePrefixName + '_' + colour + '.png\"'
    response['Expires'] = expires
    response['Cache-Control'] = "public, max-age=" + str(DELTA_SECONDS)
    return response

def galaxy(request, galaxy_id):
    session = PogsSession()
    galaxy_id = int(galaxy_id)
    galaxy = session.query(database_support.Galaxy).filter("galaxy_id=:galaxy_id").params(galaxy_id=galaxy_id).first()
    galaxy_name = galaxy.name
    if galaxy.version_number > 1:
        galaxy_name = galaxy.name + "[" + str(galaxy.version_number) + "]"
    galaxy_height = galaxy.dimension_x;
    galaxy_width = galaxy.dimension_y;
    session.close()
    
    referer = getRefererFromCookie(request)
    
    t = loader.get_template('pogs/galaxy_images.html')
    c = Context({
        'galaxy_id': galaxy_id,
        'galaxy_name': galaxy_name,
        'galaxy_width': galaxy_width,
        'galaxy_height': galaxy_height,
        'referer':          referer,
    })
    return HttpResponse(t.render(c))

def galaxyList(request, page):
    lines_per_page = 3
    galaxies_per_line = 5
    page = int(page)
    if page < 1:
        page = 1
    start = (page-1) * lines_per_page * galaxies_per_line
    next_page = None
    if page == 1:
        prev_page = None
    else:
        prev_page = page - 1
    session = PogsSession()
    galaxies = session.query(database_support.Galaxy).order_by(database_support.Galaxy.name, database_support.Galaxy.version_number).all()
    galaxy_list = []
    idx = 0
    count = 0
    galaxy_line = None
    for galaxy in galaxies:
        count = count + 1
        name = galaxy.name
        if galaxy.version_number > 1:
            name = galaxy.name + "[" + str(galaxy.version_number) + "]"
        if count < start:
            pass
        elif idx == 0:
            if len(galaxy_list) >= lines_per_page:
                next_page = page + 1
                break
            galaxy_line = GalaxyLine()
            galaxy_line.name1 = name
            galaxy_line.id1 = galaxy.galaxy_id
            galaxy_line.redshift1 = str(galaxy.redshift)
            galaxy_line.height1 = galaxy.dimension_x
            galaxy_line.width1 = galaxy.dimension_y
            galaxy_list.append(galaxy_line)
            idx = 1
        elif idx == 1:
            galaxy_line.name2 = name
            galaxy_line.id2 = galaxy.galaxy_id
            galaxy_line.redshift2 = str(galaxy.redshift)
            galaxy_line.height2 = galaxy.dimension_x
            galaxy_line.width2 = galaxy.dimension_y
            idx = 2
        elif idx == 2:
            galaxy_line.name3 = name
            galaxy_line.id3 = galaxy.galaxy_id
            galaxy_line.redshift3 = str(galaxy.redshift)
            galaxy_line.height3 = galaxy.dimension_x
            galaxy_line.width3 = galaxy.dimension_y
            idx = 3
        elif idx == 3:
            galaxy_line.name4 = name
            galaxy_line.id4 = galaxy.galaxy_id
            galaxy_line.redshift4 = str(galaxy.redshift)
            galaxy_line.height4 = galaxy.dimension_x
            galaxy_line.width4 = galaxy.dimension_y
            idx = 4
        elif idx == 4:
            galaxy_line.name5 = name
            galaxy_line.id5 = galaxy.galaxy_id
            galaxy_line.redshift5 = str(galaxy.redshift)
            galaxy_line.height5 = galaxy.dimension_x
            galaxy_line.width5 = galaxy.dimension_y
            idx = 0
    session.close()
    referer = getReferer(request)

    t = loader.get_template('pogs/galaxy_list.html')
    c = Context({
        'galaxy_list':      galaxy_list,
        'prev_page':        prev_page,
        'next_page':        next_page,
        'referer':          referer,
    })
    return HttpResponse(t.render(c))

def galaxyImage(request, galaxy_id, colour):
    imageDirName = django_image_dir

    session = PogsSession()
    galaxy_id = int(galaxy_id)
    galaxy = session.query(database_support.Galaxy).filter("galaxy_id=:galaxy_id").params(galaxy_id=galaxy_id).first()

    image = fitsimage.FitsImage()
    imagePrefixName = '{0}_{1}'.format(galaxy.name, galaxy.version_number);
    imageFileName = image.get_colour_image_path(imageDirName, imagePrefixName, colour, False)
    session.close()

    sizeBytes = os.path.getsize(imageFileName)
    file = open(imageFileName, "rb")
    myImage = file.read(sizeBytes)
    file.close()

    DELTA = datetime.timedelta(minutes=100)
    DELTA_SECONDS = DELTA.days * 86400 + DELTA.seconds
    EXPIRATION_MASK = "%a, %d %b %Y %H:%M:%S %Z"
    expires = (datetime.datetime.now()+DELTA).strftime(EXPIRATION_MASK)

    response = HttpResponse(myImage, content_type='image/png')
    response['Content-Disposition'] = 'filename=\"' + imageFileName + '\"'
    response['Expires'] = expires
    response['Cache-Control'] = "public, max-age=" + str(DELTA_SECONDS)
    return response

def galaxyParameterImage(request, galaxy_id, name):
    imageDirName = django_image_dir

    session = PogsSession()
    galaxy_id = int(galaxy_id)
    galaxy = session.query(database_support.Galaxy).filter("galaxy_id=:galaxy_id").params(galaxy_id=galaxy_id).first()

    image = fitsimage.FitsImage()
    imageFileName = '{0}_{1}_{2}.png'.format(galaxy.name, galaxy.version_number, name);
    filename = image.get_file_path(imageDirName, imageFileName, False)
    session.close()

    sizeBytes = os.path.getsize(filename)
    file = open(filename, "rb")
    myImage = file.read(sizeBytes)
    file.close()

    DELTA = datetime.timedelta(minutes=10)
    DELTA_SECONDS = DELTA.days * 86400 + DELTA.seconds
    EXPIRATION_MASK = "%a, %d %b %Y %H:%M:%S %Z"
    expires = (datetime.datetime.now()+DELTA).strftime(EXPIRATION_MASK)

    response = HttpResponse(myImage, content_type='image/png')
    response['Content-Disposition'] = 'filename=\"' + imageFileName + '\"'
    response['Expires'] = expires
    response['Cache-Control'] = "public, max-age=" + str(DELTA_SECONDS)
    return response
