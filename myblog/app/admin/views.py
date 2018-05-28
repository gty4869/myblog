from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from markdown import markdown as to_markdown

from . import blueprint
from .forms import LoginForm, UploadPostForm
from model.user import UserModel
from model.post import PostModel


@blueprint.route('/')
@login_required
def index():
    posts = PostModel.query.all()
    return render_template('admin/index.html', posts=posts)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(form.data)
    if form.validate_on_submit():
        user = UserModel.query.filter_by(name=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
        else:
            flash('滚蛋！( o｀ω′)ノ')
        return redirect(url_for('admin.index'))

    return render_template('admin/login.html', form=form)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@blueprint.route('/upload-post', methods=['POST', 'GET'])
@login_required
def upload_post():
    form = UploadPostForm()
    if form.file.data:
        file = request.files.get(form.file.name)
        try:
            tags, title, summary = [None] * 3
            markdown = []
            for line in file.stream.readlines():
                text = line.decode()

                if tags and title and summary:
                    markdown.append(text)

                if text.startswith('tags:'):
                    tags = text[len('tags:'):].strip()
                elif text.startswith('title:'):
                    title = text[len('title:'):].strip()
                elif text.startswith('summary:'):
                    summary = text[len('summary:'):].strip()

            markdown = ''.join(markdown)
            post = PostModel()
            post.title = title
            post.summary = summary
            post.markdown = markdown
            post.html = to_markdown(markdown, extensions=['fenced_code', 'codehilite(css_class=highlight)'])
            post.save()

            flash('上传成功！')
            return redirect(url_for('admin.index'))

        except UnicodeDecodeError:
            flash('要上传的博客仅支持utf8编码的md文件')
            return redirect(url_for('admin.upload_post'))

    return render_template('admin/upload_post.html', form=form)


@blueprint.route('/delete-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    return render_template('admin/delete_post.html')


@blueprint.route('/hide-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def hide_post(post_id):
    post = PostModel.query.get(post_id)
    if request.method == 'POST' and post:
        post.hidden = True
        post.save()
    return render_template('admin/hide_post.html', post=post)


@blueprint.route('/show-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def show_post(post_id):
    post = PostModel.query.get(post_id)
    if request.method == 'POST' and post:
        post.hidden = False
        post.save()
        flash('已使这篇博客对外可见')
    return redirect(url_for('admin.index'))


@blueprint.route('/replace-post/<int:post_id>', methods=['POST', 'GET'])
@login_required
def replace_post(post_id):
    return render_template('admin/replace_post.html')


@blueprint.route('/preview-post')
@login_required
def preview_post():
    return ''