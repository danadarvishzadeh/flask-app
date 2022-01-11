user_fixture = {
    'user_dana_valid': {
        'username': 'dana',
        'email': 'dana@dana.com',
        'first_name': 'dana',
        'last_name': 'danaplastiki',
        'password': '123456789'
    },
    'user_mamad_valid': {
        'username': 'mamad',
        'email': 'mamad@dana.com',
        'first_name': 'mamad',
        'last_name': 'mamadplastiki',
        'password': '123456789'
    },
    'user_dana_invalid_edit': {
        'first_name': 'mamad',
        'last_name': 'mamadplastiki',
    },
    'user_dana_valid_edit': {
        'last_name': 'mamadplastiki',
    },
    'user_dana_invalid': {
        'username': 1,
        'email': 'dana.dana.com',
        'first_name': 'dana',
        'last_name': 'danaplastiki',
        'password': '1234567'
    },
}

discussion_fixture = {
    'dana_first_discussion_valid': {
        'title': 'dana first discussion',
        'description': 'first discussion description'
    },
    'dana_first_discussion_invalid': {
        'title': 1,
        'description': 2
    },
    'dana_second_discussion_valid': {
        'title': 'dana second discussion',
        'description': 'second discussion description'
    },
    'mamad_first_discussion_valid': {
        'title': 'mamad first discussion',
        'description': 'first discussion description'
    },
    'mamd_second_discussion_valid': {
        'title': 'mamad second discussion',
        'description': 'second discussion description'
    },
}

post_fixture = {
    'discussion1_post1': {
        'body': 'discussion1 post1 body',
    },
    'discussion1_post2': {
        'body': 'discussion1 post2 body',
    },
    'discussion1_post2_invalid': {
        'body': 5,
    },
    'discussion2_post1': {
        'body': 'discussion2 post1 body',
    },
    'discussion2_post2': {
        'body': 'discussion2 post2 body',
    },
}

invitation_fixture = {
    'invite': {
        'body': 'It would be nice if you join me.'
    }
}