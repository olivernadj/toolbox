#!/usr/bin/env ruby

require 'optparse'
require 'open-uri'
require 'json'
require 'csv'

options = {}
ARGV << '-h' if ARGV.empty?
OptionParser.new do |opts|
  opts.banner = "This script retrieves all members from a slack channel\nUsage: #{$PROGRAM_NAME} [options]"
  opts.on('-t', '--token Slack tocken', 'How to get: https://api.slack.com/custom-integrations/legacy-tokens') { |v| options[:token] = v }
  opts.on('-g', '--group Group ID', 'How to get: https://api.slack.com/methods/groups.list') { |v| options[:group_id] = v }
  opts.on('-c', '--channel Channel ID', 'How to get: https://api.slack.com/methods/channels.list') { |v| options[:channel_id] = v }
end.parse!

unless options[:token].nil?
  info = nil
  info = JSON.parse(open("https://slack.com/api/channels.info?token=" + options[:token] + "&channel=" + options[:channel_id]).read) unless options[:channel_id].nil?
  info = JSON.parse(open("https://slack.com/api/groups.info?token=" + options[:token] + "&channel=" + options[:group_id]).read) unless options[:group_id].nil?   
  if info
    csv_string = CSV.generate do |csv|
      csv_header = ['first_name','last_name','email']
      csv << csv_header
      info['group']['members'].each do |member_id|
        profile = JSON.parse(open("https://slack.com/api/users.info?token=" + options[:token] + "&user=" + member_id).read)['user']
        csv << profile['profile'].select { |key,_| csv_header.include? (key) }.values unless profile['deleted']
      end
    end
    puts csv_string
  end
end 

