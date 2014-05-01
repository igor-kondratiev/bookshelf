# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BookDistance'
        db.create_table(u'books_bookdistance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='first_book', to=orm['books.Book'])),
            ('second_book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='second_book', to=orm['books.Book'])),
            ('distance', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'books', ['BookDistance'])


    def backwards(self, orm):
        # Deleting model 'BookDistance'
        db.delete_table(u'books_bookdistance')


    models = {
        u'books.author': {
            'Meta': {'object_name': 'Author'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'books.book': {
            'Meta': {'object_name': 'Book'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['books.Author']"}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['books.BookGenre']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_file': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        u'books.bookdistance': {
            'Meta': {'object_name': 'BookDistance'},
            'distance': ('django.db.models.fields.FloatField', [], {}),
            'first_book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'first_book'", 'to': u"orm['books.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'second_book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'second_book'", 'to': u"orm['books.Book']"})
        },
        u'books.bookgenre': {
            'Meta': {'object_name': 'BookGenre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['books']