# -*- coding: utf-8 -*-
"""

"""
import time

from natrixclient.command.nhttp import execute as http_execute
from natrixclient.common import const

from natrixclient.bin import ln
from natrixclient.bin import logger


def parse_http_request_parameters(args):
    parameters = dict()
    if args.interface:
        parameters["interface"] = args.interface
    parameters["allow_redirects"] = args.allow_redirects
    parameters["max_redirects"] = args.max_redirects
    if args.auth_type:
        parameters["auth_type"] = args.auth_type
    if args.auth_user:
        parameters["auth_user"] = args.auth_user
        auths = args.auth_user.split(":")
        if len(auths) != 2:
            logger.error("Error: auth_user format should be like username:password")
            exit(0)
    parameters["timeout"] = args.timeout
    parameters["connect_timeout"] = args.connect_timeout
    # parameters["request_timeout"] = args.request_timeout
    parameters["dns_cache_timeout"] = args.dns_cache_timeout
    parameters["fresh_connect"] = args.fresh_connect
    if args.http_header:
        parameters["http_header"] = args.http_header
    if args.http_body:
        parameters["http_body"] = args.http_body
    parameters["save_response_header"] = args.save_response_header
    parameters["save_response_body"] = args.save_response_body
    parameters["terminal_request_receive_time"] = time.time()
    # logger
    parameters["logger"] = ln
    return parameters


def parse_http_response_parameters():
    parameters = dict()
    parameters["storage_type"] = const.StorageMode.CONSOLE
    # logger
    parameters["logger"] = ln
    return parameters


def parse_http_get(args):
    destination = args.destination
    http_execute(const.HttpOperation.GET, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_post(args):
    destination = args.destination
    http_execute(const.HttpOperation.POST, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_put(args):
    destination = args.destination
    http_execute(const.HttpOperation.PUT, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


def parse_http_delete(args):
    destination = args.destination
    http_execute(const.HttpOperation.DELETE, destination, parse_http_request_parameters(args),
                 parse_http_response_parameters())


# subcommand - HTTP
def console_http(subparsers):
    parser_http = subparsers.add_parser("http",
                                        help='Natrix Client Sub Command - http. '
                                             'such as GET, POST, PUT, DELETE ans so on')
    # Sub Command
    httpsubparsers = parser_http.add_subparsers(title="Natrix Client HTTP Sub Commands",
                                                description="Natrix Client HTTP Sub Commands.",
                                                help='Help Information About the Natrix Client HTTP Sub Command')
    # sub command - GET
    parser_http_get = httpsubparsers.add_parser('get',
                                                help='Natrix Client HTTP Sub Command - GET.')
    parser_http_get.set_defaults(func=parse_http_get)
    # sub command - POST
    parser_http_post = httpsubparsers.add_parser('post',
                                                 help='Natrix Client HTTP Sub Command - POST.')
    parser_http_post.set_defaults(func=parse_http_post)
    # sub command - PUT
    parser_http_put = httpsubparsers.add_parser('put',
                                                help='Natrix Client HTTP Sub Command - PUT.')
    parser_http_put.set_defaults(func=parse_http_put)
    # sub command - DELETE
    parser_http_delete = httpsubparsers.add_parser('delete',
                                                   help='Natrix Client HTTP Sub Command - DELETE.')
    parser_http_delete.set_defaults(func=parse_http_delete)
    # common arguments
    parser_http.add_argument('destination',
                             help="http destination, url or ip.")
    # HTTP版本
    # parser_http.add_argument("--http-version",
    #                          help="HTTP version, support 1.0 / 1.1 / 2.0")
    # 接口
    parser_http.add_argument("-i",
                             "--interface",
                             help="user can use dedicated network interface.")
    # 重定向
    # --allow_redirects -R
    parser_http.add_argument("--allow-redirects",
                             dest="allow_redirects",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_ALLOW_REDIRECTS,
                             help="Allow Redirects, Default is {}.".format(const.HTTP_ALLOW_REDIRECTS))
    # 最大重定向数
    # --max_redirects -r
    parser_http.add_argument("--max-redirects",
                             dest="max_redirects",
                             type=int,
                             default=const.HTTP_MAX_REDIRECTS,
                             help="Set Max Redirects. Default is {}.".format(str(const.HTTP_MAX_REDIRECTS)))
    # 安全验证
    # --authentication-type -a
    parser_http.add_argument("-a",
                             "--auth-type",
                             dest="auth_type",
                             default=const.HTTP_AUTH_TYPE,
                             help="Authentication Type. support basic")
    # 安全验证
    # --authentication-content -c
    parser_http.add_argument("-u",
                             "--auth-user",
                             dest="auth_user",
                             help="Specify the user name and password to use for server authentication, "
                                  "for basic_auth, like guest:guest")
    # 超时时间
    parser_http.add_argument("-t",
                             "--timeout",
                             dest="timeout",
                             default=const.HTTP_TIMEOUT,
                             help="Set an expiration time.")
    # 连接超时时间
    parser_http.add_argument("--connect-timeout",
                             dest="connect_timeout",
                             default=const.HTTP_CONNECT_TIMEOUT,
                             help="HTTP connect timeout, HTTP连接超时. "
                                  "default is {} seconds".format(str(const.HTTP_CONNECT_TIMEOUT)))
    # 请求超时时间
    # parser_http.add_argument("--request-timeout",
    #                          dest="request_timeout",
    #                          default=const.HTTP_REQUEST_TIMEOUT,
    #                          help="HTTP request timeout, HTTP请求超时. "
    #                               "default is {} seconds".format(str(const.HTTP_REQUEST_TIMEOUT)))

    # DNS信息保存时间
    parser_http.add_argument("--dns-cache-timeout",
                             dest="dns_cache_timeout",
                             default=const.HTTP_DNS_CACHE_TIMEOUT,
                             help="DNS information timeout, DNS信息保存时间. "
                                  "default is {} seconds".format(str(const.HTTP_DNS_CACHE_TIMEOUT)))
    # 强制获取新连接
    parser_http.add_argument("--fresh-connect",
                             dest="fresh_connect",
                             action="store_true",
                             default=const.HTTP_FRESH_CONNECT,
                             help="Force to set new HTTP connection, 强制获取新连接. "
                                  "default is {}".format(str(const.HTTP_FRESH_CONNECT)))
    # 头部信息
    parser_http.add_argument("-H",
                             "--http-header",
                             dest="http_header",
                             help="Custom HTTP Headers.")
    # BODY信息
    parser_http.add_argument("-D",
                             "--http-body",
                             dest="http_body",
                             help="Custom HTTP Body.")
    # 保存response头部信息
    parser_http.add_argument("--save-response-header",
                             dest="save_response_header",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_SAVE_RESPONSE_HEADER,
                             help="Save Response Header Information in Return Result.")
    # 保存response body 信息
    parser_http.add_argument("--save-response-body",
                             dest="save_response_body",
                             # type=bool,
                             action="store_true",
                             default=const.HTTP_SAVE_RESPONSE_BODY,
                             help="Save Response Body Information in Return Result.")
