# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Author'
        db.create_table(u'books_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'books', ['Author'])

        # Adding model 'BookGenre'
        db.create_table(u'books_bookgenre', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal(u'books', ['BookGenre'])

        # Adding model 'Book'
        db.create_table(u'books_book', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['books.Author'])),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('text_file', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal(u'books', ['Book'])

        # Adding M2M table for field genres on 'Book'
        m2m_table_name = db.shorten_name(u'books_book_genres')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('book', models.ForeignKey(orm[u'books.book'], null=False)),
            ('bookgenre', models.ForeignKey(orm[u'books.bookgenre'], null=False))
        ))
        db.create_unique(m2m_table_name, ['book_id', 'bookgenre_id'])


    def backwards(self, orm):
        # Deleting model 'Author'
        db.delete_table(u'books_author')

        # Deleting model 'BookGenre'
        db.delete_table(u'books_bookgenre')

        # Deleting model 'Book'
        db.delete_table(u'books_book')

        # Removing M2M table for field genres on 'Book'
        db.delete_table(db.shorten_name(u'books_book_genres'))


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
        u'books.bookgenre': {
            'Meta': {'object_name': 'BookGenre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['books']