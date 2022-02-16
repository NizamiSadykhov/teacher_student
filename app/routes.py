import logging

from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.urls import url_parse

from app import app
from flask import render_template, redirect, url_for, request

from app.forms import RegistrationForm, LoginForm, ChangeMarkForm, EditProfileFormStudent, AddLrForm, \
    EditProfileFormTeacher
from app.models import User
from config import conn


@app.route('/')
def mainPage():
    return redirect(url_for('login'))


@app.route('/student/<username>/<subject>', methods=['GET', 'POST'])
@login_required
def student_lr(username, subject):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM student")
    usernameList = cursor.fetchall()
    lr_list = get_student_lr(subject, username)
    for _username in usernameList:
        if _username[0] == username:
            id = get_id_by_studentUsername(username)
            user = User(id)
            user.set_status('student')
            edit_profile_student_form = EditProfileFormStudent()
    return render_template('student_lr.html', user=user, lr_list=lr_list, subject=subject,
                           form=edit_profile_student_form)


def get_student_lr(subject, student):
    list_lr = []
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM lr WHERE id_subject = {}".format(get_id_by_subject(subject)))
    lrs = cursor.fetchall()
    for lr in lrs:
        dict_lr = {'name': lr[0], 'mark': get_markLR_by_student(get_id_by_LR(lr[0]), student),
                   'date': get_markDate(get_id_by_LR(lr[0]), student)}
        list_lr.append(dict_lr)
    return list_lr


@app.route('/student/<username>', methods=['GET', 'POST'])
@login_required
def student(username):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM student")
    usernameList = cursor.fetchall()
    subject_list = get_student_subject(username)
    for _username in usernameList:
        if _username[0] == username:
            id = get_id_by_studentUsername(username)
            user = User(id)
            user.set_status('student')
            edit_profile_student_form = EditProfileFormStudent()
            if edit_profile_student_form.validate_on_submit():
                update_student_profile(edit_profile_student_form, username)
    return render_template('student.html', user=user, subject_list=subject_list, form=edit_profile_student_form)


def update_student_profile(form, username):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM student WHERE login = '{}'".format(username))
    id_student = cursor.fetchone()
    try:
        cursor.execute(
            "UPDATE student SET name = %(name)s, email = %(email)s, password = %(password)s WHERE id = %(id_student)s",
            {
                'name': form.name.data,
                'email': form.email.data,
                'password': form.password.data,
                'id_student': id_student[0]
            })
        conn.commit()
    except:
        logging.exception('')
        cursor.execute("ROLLBACK")
        conn.commit()


def update_teacher_profile(form, username):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
    id_teacher = cursor.fetchone()
    try:
        cursor.execute(
            "UPDATE teacher SET name = %(name)s, email = %(email)s, password = %(password)s WHERE id = %(id_teacher)s",
            {
                'name': form.name.data,
                'email': form.email.data,
                'password': form.password.data,
                'id_teacher': id_teacher[0]
            })
        conn.commit()
    except:
        logging.exception('')
        cursor.execute("ROLLBACK")
        conn.commit()


def get_student_subject(username):
    list_subject = []
    cursor = conn.cursor()
    id_group = get_groupID_by_userID(get_id_by_studentUsername(username))
    cursor.execute("SELECT id_subject FROM all_subject_group WHERE id_group = {}".format(id_group))
    subjects = cursor.fetchall()
    for subject in subjects:
        dict_subject = {'name': get_subjectName_by_subjectID(subject[0]),
                        'count': len(get_student_lr(get_subjectName_by_subjectID(subject[0]), username))}
        list_subject.append(dict_subject)
    return list_subject


def get_groupID_by_userID(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id_group FROM student WHERE id = {}".format(user_id))
    group_id = cursor.fetchone()
    return group_id[0]


def get_subjectName_by_subjectID(subject_id):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM subject WHERE id = {}".format(subject_id))
    subjectName = cursor.fetchone()
    return subjectName[0]


@app.route('/teachers/<username>', methods=['GET', 'POST'])
@login_required
def teacher(username):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM teacher")
    usernameList = cursor.fetchall()
    teacher_subject_List = get_teacher_subject(username)
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            user.set_status('teacher')
            edit_profile_teacher_form = EditProfileFormTeacher()
            if edit_profile_teacher_form.validate_on_submit():
                update_teacher_profile(edit_profile_teacher_form, username)
    return render_template('teacher.html', user=user, teacher_subject_List=teacher_subject_List,
                           form=edit_profile_teacher_form)


def get_teacher_subject(username):
    teacher_subject_List = []
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
    id_teacher = cursor.fetchone()
    cursor.execute("SELECT name FROM teachersubject WHERE id_teacher = '{}'".format(id_teacher[0]))
    teacher_subjectS = cursor.fetchall()
    for teacher_subject in teacher_subjectS:
        teacher_subject_Dict = {'name': teacher_subject[0]}
        teacher_subject_List.append(teacher_subject_Dict)
    return teacher_subject_List


@app.route('/teachers/<username>/<subject>', methods=['GET', 'POST'])
@login_required
def subject(username, subject):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM teacher")
    usernameList = cursor.fetchall()
    subject_group = get_subject_group(subject)
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            user.set_status('teacher')
            add_lr_form = AddLrForm()
            edit_profile_teacher_form = EditProfileFormTeacher()
            if add_lr_form.validate_on_submit():
                add_new_lr(add_lr_form.name.data, subject)
            if edit_profile_teacher_form.validate_on_submit():
                update_teacher_profile(edit_profile_teacher_form, username)
    return render_template('subject.html', user=user, subject_group_List=subject_group, subject=subject,
                           form=add_lr_form, form2=edit_profile_teacher_form)


def add_new_lr(name_lr, subject):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO lr VALUES ((SELECT MAX(id) + 1 FROM lr), %(id_subject)s, %(name)s)",
                       {
                           'id_subject': get_id_by_subject(subject),
                           'name': name_lr
                       })
        conn.commit()
    except:
        logging.exception('')
        cursor.execute("ROLLBACK")
        conn.commit()


def get_subject_group(subject):
    subject_group_List = []
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subject WHERE name = '{}'".format(subject))
    id_subject = cursor.fetchone()
    cursor.execute("SELECT id_group FROM all_subject_group WHERE id_subject = '{}'".format(id_subject[0]))
    groups = cursor.fetchall()
    for group in groups:
        subject_group_Dict = {'name': get_group_by_id(group[0])}
        subject_group_List.append(subject_group_Dict)
    return subject_group_List


def get_group_by_id(id):
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM _group WHERE id = '{}'".format(id))
    group = cursor.fetchone()
    return group[0]


@app.route('/teachers/<username>/<subject>/<group>', methods=['GET', 'POST'])
@login_required
def group(username, subject, group):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM teacher")
    usernameList = cursor.fetchall()
    studets_names = get_students_names(group)
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            user.set_status('teacher')
            edit_profile_teacher_form = EditProfileFormTeacher()
            if edit_profile_teacher_form.validate_on_submit():
                update_teacher_profile(edit_profile_teacher_form, username)
    return render_template('group.html', user=user, group=group, studets_names_List=studets_names, subject=subject,
                           form=edit_profile_teacher_form)


def get_students_names(group):
    student_names_List = []
    cursor = conn.cursor()
    cursor.execute("SELECT name, login FROM student WHERE id_group = '{}'".format(get_id_by_group(group)))
    student_names = cursor.fetchall()
    for student_name in student_names:
        students_names_Dict = {'name': student_name[0], 'username': student_name[1]}
        student_names_List.append(students_names_Dict)
    return student_names_List


def get_id_by_group(group):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM _group WHERE number = '{}'".format(group))
    id = cursor.fetchone()
    return id[0]


@app.route('/teachers/<username>/<subject>/<group>/<student>', methods=['GET', 'POST'])
@login_required
def studentLR(username, subject, group, student):
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM teacher")
    usernameList = cursor.fetchall()
    studets_LR = get_student_LR(student, subject)
    change_mark_form = ChangeMarkForm()
    for _username in usernameList:
        if _username[0] == username:
            cursor.execute("SELECT id FROM teacher WHERE login = '{}'".format(username))
            id = cursor.fetchone()
            user = User(id[0])
            user.set_status('teacher')
            edit_profile_teacher_form = EditProfileFormTeacher()
            if edit_profile_teacher_form.validate_on_submit():
                update_teacher_profile(edit_profile_teacher_form, username)
            if change_mark_form.validate_on_submit():
                update_mark(change_mark_form.mark.data, change_mark_form.date.data, change_mark_form.LR_name.data,
                            student)
    return render_template('lr.html', form=change_mark_form, user=user, group=group, student=student,
                           studets_LR_List=studets_LR, subject=subject, form2=edit_profile_teacher_form)


def update_mark(mark, date, lr_name, student):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM mark_lr WHERE id_lr = {} and id_student = {}".format(get_id_by_LR(lr_name),
                                                                                        get_id_by_studentUsername(
                                                                                            str(student))))
    id = cursor.fetchone()
    if id is not None:
        try:
            cursor.execute("UPDATE mark_lr SET mark = %(mark)s, mark_data = %(date)s "
                           "WHERE id_lr = %(lr_id)s and id_student = %(id_student)s",
                           {'mark': mark,
                            'date': date,
                            'lr_id': get_id_by_LR(lr_name),
                            'id_student': get_id_by_studentUsername(str(student))
                            })
            conn.commit()
        except:
            logging.exception('')
            cursor.execute("ROLLBACK")
            conn.commit()
    else:
        try:
            cursor.execute(
                "INSERT INTO mark_lr VALUES ((SELECT MAX(id) + 1 FROM mark_lr), %(mark)s, %(date)s, %(lr_id)s, "
                "%(id_student)s)",
                {'mark': mark,
                 'date': date,
                 'lr_id': get_id_by_LR(lr_name),
                 'id_student': get_id_by_studentUsername(str(student))
                 })
            conn.commit()
        except:
            logging.exception('')
            cursor.execute("ROLLBACK")
            conn.commit()


def get_student_LR(student, subject):
    student_LR_List = []
    cursor = conn.cursor()
    cursor.execute("select lr.id from lr inner join subject on lr.id_subject = subject.id where id_subject = {}".format(
        get_id_by_subject(subject)))
    LRs = cursor.fetchall()
    for LR in LRs:
        LR_Dict = {'name': get_LR_by_id(LR[0]), 'mark': get_markLR_by_student(LR[0], student),
                   'date': get_markDate(LR[0], student)}
        student_LR_List.append(LR_Dict)
    return student_LR_List


def get_markLR_by_student(id_lr, student):
    print('AAA', student)
    cursor = conn.cursor()
    cursor.execute("Select mark from mark_lr where id_lr = {} and id_student = {}".format(id_lr,
                                                                                          get_id_by_studentUsername(
                                                                                              student)))
    mark = cursor.fetchone()
    if mark is None:
        return ('Оценки нет')
    return mark[0]


def get_markDate(id_lr, student):
    cursor = conn.cursor()
    cursor.execute("Select mark_data from mark_lr where id_lr = {} and id_student = {}".format(id_lr,
                                                                                               get_id_by_studentUsername(
                                                                                                   student)))
    date = cursor.fetchone()
    if date is None:
        return (" ")
    return time(date[0])


def time(time):
    time = str(time)
    return time[0:10]


def get_id_by_subject(subject):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM subject WHERE name = '{}'".format(subject))
    subj = cursor.fetchone()
    return subj[0]


def get_id_by_LR(LR_name):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM lr WHERE name = '{}'".format(LR_name))
    id_LR = cursor.fetchone()
    return id_LR[0]


def get_LR_by_id(LR):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM lr WHERE id = '{}'".format(LR))
    lr = cursor.fetchone()
    return lr[0]


def get_id_by_studentUsername(student_username):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM student WHERE login = '{}'".format(student_username))
    id = cursor.fetchone()
    return id[0]


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     if current_user.status == 'teacher':
    #         return redirect(url_for('teacher'), username = current_user.username)
    #     if current_user.status == 'student':
    #         return redirect(url_for('student'), username = current_user.username)
    login_form = LoginForm()
    if login_form.validate_on_submit():
        cursor = conn.cursor()
        username = login_form.username.data
        password = login_form.password.data
        if login_form.who_are_you.data == 'Student':
            cursor.execute("SELECT * FROM student ")
            students = cursor.fetchall()
            for student in students:
                if student[1] == username and student[5] == password:
                    user = User(student[0])
                    login_user(user, remember=login_form.remember_me.data)
                    user.set_status('student')
                    return redirect(url_for('student', username=user.username))
        elif login_form.who_are_you.data == 'Teacher':
            cursor.execute("SELECT * FROM teacher ")
            teachers = cursor.fetchall()
            for teacher in teachers:
                if teacher[1] == username and teacher[6] == password:
                    user = User(teacher[0])
                    login_user(user, remember=login_form.remember_me.data)
                    user.set_status('teacher')
                    return redirect(url_for('teacher', username=user.username))
    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form_register = RegistrationForm()
    group_List = createGroupList()
    if form_register.validate_on_submit():
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO student (id, login, name, id_group, password, email) "
                           "VALUES ((SELECT MAX(id) + 1 FROM student), %(username)s, %(name)s, %(id)s, %(password)s, %(email)s)",
                           {'username': form_register.Username.data,
                            'name': form_register.Name.data,
                            'id': get_id_by_group(form_register.Group.data),
                            'password': str(form_register.password.data),
                            'email': form_register.Email.data})
            conn.commit()
        except:
            logging.exception('')
            cursor.execute("ROLLBACK")
            conn.commit()
    return render_template('register.html', title='Register', form=form_register, groups=group_List)


def createGroupList():
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM _group")
    List = cursor.fetchall()
    group_List = []
    for group in List:
        dict_University = {'number': group[0]}
        group_List.append(dict_University)
    return group_List


def get_id_by_group(number_group):
    if number_group is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM _group WHERE number = '{}'".format(number_group))
        id_group = cursor.fetchone()
        return id_group[0]


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
