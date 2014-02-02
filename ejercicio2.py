#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Autentificación mínima con
# sesiones
# dai ugr.es Oct-13

import web
from web.contrib.template import render_mako
from web import form
import pymongo
import feedparser
import tweepy
from mako.template import Template
from mako.lookup import TemplateLookup
from pymongo import *



# Para poder usar sesiones con web.py
web.config.debug = False

#Nuestra base de datos
#client = MongoClient()
#db = client['test-database']
#collection = db.test_collection
conexion = Connection("127.0.0.1",27017)
database = conexion["my_db"]
col = database["my_col"]

#Nuestra rss
rss_url = "http://ep00.epimg.net/rss/elpais/portada.xml"
feed = feedparser.parse( rss_url )

# Consumer keys and access tokens, used for OAuth
consumer_key = 'nnLHDlxw4Z1UQdDLJAcg'
consumer_secret = '9pYSnfzjcfAvreQ8gBguupEKwvWvHZM9jPejhvuwV9E'
access_token = '36126409-QVkWKqeavD5SN3VVbdiZSSzwPVdf3hcXgDtYYV1I6'
access_token_secret = 'JxKNOEZtI62Y8Kpjoly8nEngqYRQtsv68coM3tGac7yzT'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
# Creation of the actual interface, using authentication
api = tweepy.API(auth)
# https://dev.twitter.com/docs/api/1.1/get/search/tweets


urls = (
  '/', 'inicio',
  '/login', 'login',
  '/logout', 'logout',
  '/clasificacion.html', 'clasificacion',
  '/encuentros.html', 'encuentros',
  '/inicio.html', 'inicio',
  '/formulario.html', 'formulario',
  '/registro', 'registro',
  '/encuesta.html', 'encuesta',
  '/jugadores', 'jugadores',
  '/mundial.html', 'mundial',
  
)

app = web.application (urls, locals())

session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'usuario':''})

# Templates de mako
render = render_mako (
	directories=['miPagina'],
	input_encoding = 'utf-8',
	output_encoding = 'utf-8')


login_form = form.Form (
	form.Textbox ('username', form.notnull, description='Usuario:'),
	form.Password ('password', form.notnull, description=u'Contrasenia:'),
	form.Button ('Login'),
)

formulariooo=form.Form(
	form.Textbox("nombre", form.notnull, description="nombre:",),
	form.Textbox("apellidos", form.notnull, description="apellidos:"),
	form.Textbox("dni", form.notnull, description="dni:"),
	form.Textbox("correo", form.notnull, form.regexp(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b','Email no valido') ,description="correo:"),
	form.Dropdown('dia', range(1, 32), description="Dia:"),
	form.Dropdown('mes', [('1', 'enero'), ('2', 'febrero'), ('3', 'marzo'), ('4', 'abril'), ('5', 'mayo'), ('6', 'junio'), ('7', 'julio'), ('8', 'agosto'), ('9', 'septiembre'), ('10', 'octubre'), ('11', 'noviembre'), ('12', 'diciembre')], description="Mes"),
	form.Dropdown('anio', range(1970, 2014), description="Anio"),
	form.Password("clave1", form.notnull, form.Validator('Debe tener mas de 7 caracteres', lambda x:len(x)>7), description="Clave1"),
	form.Button("Enviar formulario:"),
	validators = [form.Validator("Fecha incorrecta", lambda i: not((i.mes == '2' and i.dia == '31') or (i.mes == '2' and i.dia == '30') or (i.mes == '4' and i.dia == '30') or (i.mes == '6' and i.dia == '31') or (i.mes == '9' and i.dia == '31') or (i.mes == '11' and i.dia == '31') or (i.mes == '2' and i.dia == '29' and anio % 4 == 0)))],
)

formulario_goles=form.Form(
	form.Dropdown('CR7', range(0, 100), description="Cristiano Ronaldo:"),
	form.Dropdown('Messi', range(0, 100), description="Messi:"),
	form.Dropdown('Costa', range(0, 100), description="Diego Costa:"),
	form.Dropdown('Griezmann', range(0, 100), description="Griezmann:"),
	form.Dropdown('Alexis', range(0, 100), description="Alexis:"),
	form.Button("Contestar:"),
)

def comprueba_identificacion (): 
	usuario = session.usuario   # Devuelve '' cuando no esta identificado
	return usuario              # que es el usuario inicial 
                                  


class logout:
	def GET(self):
		usuario = session.usuario
		session.kill()
		form = login_form ()
		return render.inicio (form=form, usuario='Nadie', urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", formularioLogin=form.render())


class login:
	def POST(self):
		form = login_form ()
		if not form.validates ():
			return render.inicio (form=form, usuario='Nadie', urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", formularioLogin=form.render())
		else:
			i = web.input()
			usuario  = i.username
			password = i.password
			var=database.col.find_one({'_nombre':usuario})
			num=database.col.find({'_nombre':usuario}).count()
			
			if(num==1):
				session.password = password
				if (var['clave1']==password):
					session.usuario = usuario
					return web.seeother('/')
				else:
					return render.inicio (form=form, mensaje='Clave incorrecta', urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", formularioLogin=form.render())
			#if (db.posts.find_one({'_nombre': usuario})):
				#session.usuario=usuario
				#return web.seeother('/')   # Redirige a inicio
			else:	
				form = login_form ()
				return render.inicio (form=form, mensaje='Usuario incorrecto', urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", formularioLogin=form.render())


# Comprueba que el usuario este identificado
# sino se lo pide
class inicio:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			return render.inicio2(usuario=usuario, urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", var="Bienvenido %s" % usuario)
		else:
			form = login_form ()
			return render.inicio(form=form, usuario=usuario, urlImagen1="static/images/casillas1.jpg", noticiaIker="La gran mayoria apuesta por Iker", noticiaIker2="Despues de su exhibicion ante la Juve, Iker Casillas recupera credito entre los aficionados madridistas. Hasta el punto de que cuatro de cada cinco ven al primer capitan blanco en mejor forma que a Diego Lopez.", neymar="'Ney' quiere estrenarse en Europa", urlImagen2="static/images/barcelona.jpg", noticiaNeymar="Neymar aun no sabe lo que es marcar en la Champions y cuenta hoy ante el Milan (20:45 h) con una ocasion especial para empezar a hacer historia en Europa.", urlImagen3="static/images/lorenzo.jpg", noticiaLorenzo="Jorge Lorenzo ya prepara el decisivo Gran Premio de la Comunidad Valenciana, donde podria conseguir su tercera corona de MotoGP, a la que llega pleno de moral pese a partir en desventaja respecto a Marquez.", urlImagen4="static/images/gasol.jpg", noticiaGasol="Pau Gasol no se esconde y se muestra critico con el juego mostrado por los Lakers en la derrota ante los Mavericks, pero con la esperanza de mejorar en los proximos compromisos. El ala-pivot espaniol atendio a MARCA y analizo lo sucedido.", urlImagen5="static/images/aragones.jpg", noticiaAragones="Luis Aragones hablo, en una entrevista concedida al diario 'ABC', del estado de forma del Atletico de Madrid: Ahora mismo es junto al Bayern el equipo que mejor juega de Europa. Es el que mejor defiende. Quiza no haga el futbol mas brillante, pero si muy bonito.", formularioLogin=form.render())  
			
class clasificacion:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			return render.clasificacion2(usuario=usuario, nombre1="C.Ronaldo", var="Bienvenido %s" % usuario)
		else:
			form = login_form ()
			return render.clasificacion(form=form, usuario=usuario, nombre1="C.Ronaldo", formularioLogin=form.render())  
			
class encuentros:
	def GET(self):
		usuario = comprueba_identificacion () 
		#valor = len(feed['entries'])	 
		titulo1=feed.entries[0].title
		link1=feed.entries[0].link
		titulo2=feed.entries[1].title
		link2=feed.entries[1].link
		titulo3=feed.entries[2].title
		link3=feed.entries[2].link
		
		tweets = api.search(q='#granada')
		
		a1=tweets[0].author.name
		v1=tweets[0].text
		
		a2=tweets[1].author.name
		v2=tweets[1].text
			
		if usuario:
			return render.encuentros2(usuario=usuario, var="Bienvenido %s" % usuario, var1=titulo1, l1=link1, var2=titulo2, l2=link2, var3=titulo3, l3=link3, au1=a1, p1=v1, au2=a2, p2=v2)
		else:
			form = login_form ()
			return render.encuentros(form=form, usuario=usuario, formularioLogin=form.render(), var1=titulo1, l1=link1, var2=titulo2, l2=link2, var3=titulo3, l3=link3, au1=a1, p1=v1, au2=a2, p2=v2) 
			
class clasificacion:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			return render.clasificacion2(usuario=usuario, nombre1="C.Ronaldo", equipo1="R.Madrid", goles1="17", nombre2="Diego Costa", equipo2="At.Madrid", goles2="15", nombre3="Messi", equipo3="Barcelona", goles3="10", nombre4="Villa", equipo4="At.Madrid", goles4="9", nombre5="Alexis", equipo5="Barcelona", goles5="9", var="Bienvenido %s" % usuario)
		else:
			form = login_form ()
			return render.clasificacion(form=form, usuario=usuario, nombre1="C.Ronaldo", equipo1="R.Madrid", goles1="17", nombre2="Diego Costa", equipo2="At.Madrid", goles2="15", nombre3="Messi", equipo3="Barcelona", goles3="10", nombre4="Villa", equipo4="At.Madrid", goles4="9", nombre5="Alexis", equipo5="Barcelona", goles5="9", formularioLogin=form.render())  
			
class formulario:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			var=database.col.find_one({'_nombre':session.usuario})
			return render.formulario2(var="Bienvenido %s " % usuario, f_registro="Nombre: %s </br> Apellidos: %s </br> Dni: %s </br> Dia de nacimiento: %s </br> Mes de nacimiento: %s </br> Anio de nacimiento %s </br>" % (str(session.usuario), str(var['_apellidos']), str(var['_dni']), str(var['_dia']), str(var['_mes']), str(var['_anio'])))
		else:
			form = login_form ()
			form2 = formulariooo()
			return render.formulario(formularioLogin=form.render(), formularioDatos=form2.render()) 		
		
class registro:
	def POST(self):
		form=login_form()
		form2=formulariooo()
		val=form2.validates()
		if (not val):
			return render.formulario(formularioLogin=form.render(),formularioDatos=form2.render())		
		else:
			entrada=web.input()
			nombre=entrada.nombre
			apellidos=entrada.apellidos
			dni=entrada.dni
			correo=entrada.correo
			dia=entrada.dia
			mes=entrada.mes
			anio=entrada.anio
			clave1=entrada.clave1
			post = {"_nombre": nombre,
 	        "_apellidos": apellidos,
	        "_dni": dni,
	        "_correo": correo,
	        "_dia": dia,
	        "_mes": mes,
	        "_anio": anio,
	        "clave1": clave1}
			#posts = db.posts
			#post_id = posts.insert(miColeccion)
			database.col.insert(post)
			return web.seeother('/formulario.html')

class encuesta:
	def GET(self):
		usuario = comprueba_identificacion () 
		form3 = formulario_goles()
		return render.encuesta2(usuario=usuario, var="Bienvenido %s " % usuario, formularioGoles=form3.render())	
			
class jugadores:
	def POST(self):
		usuario = comprueba_identificacion () 
		form3=formulario_goles()
		entrada1=web.input()
		golesR=entrada1.CR7
		golesM=entrada1.Messi
		golesC=entrada1.Costa
		golesG=entrada1.Griezmann
		golesA=entrada1.Alexis
		return render.encuesta(usuario=usuario, var="Bienvenido %s " % usuario, formularioGoles=form3.render(), v1=golesR, v2=golesM, v3=golesC, v4=golesG, v5=golesA)	
		
class mundial:
	def GET(self):
		usuario = comprueba_identificacion () 
		if usuario:
			return render.mundial2(usuario=usuario, var="Bienvenido %s" % usuario)
		else:
			form = login_form ()
			return render.mundial(form=form, usuario=usuario, formularioLogin=form.render()) 
		
		
		
if __name__ == "__main__":
    app.run()	

