from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleSerializer, CommentSerializer

#게시물 출력 생성성
@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == 'GET':
        articles = Article.objects.select_related('user').order_by('-created_at')
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data)

#게시물 상세보기및 생성 삭제
@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(['GET', 'PUT', 'DELETE'])
def article_detail(request, article_id):
    article = get_object_or_404(Article.objects.select_related('user'), id=article_id)
    if request.method == 'GET':
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    if request.user != article.user and (request.method == 'PUT' or request.method == 'DELETE'):
        return Response({'detail': '수정 또는 삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = ArticleSerializer(instance=article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
    if request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#게시물 댓글
@permission_classes([IsAuthenticatedOrReadOnly])
@api_view(['GET', 'POST'])
def article_comments(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.method == 'GET':
        comments = article.comment_set.select_related('user').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer= CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, article_id=article_id) 
            return Response(serializer.data)

#게시물 댓글 삭제수정
@permission_classes([IsAuthenticated]) 
@api_view(['GET', 'PUT', 'DELETE'])
def article_comment_detail(request, article_id, comment_id):
    comment = get_object_or_404(Comment.objects.select_related('user'), id=comment_id, article_id=article_id)
    if request.method == 'GET': 
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    if request.user != comment.user and (request.method == 'PUT' or request.method == 'DELETE'):
        return Response({'detail': '댓글 수정 또는 삭제 권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
    if request.method == 'PUT':
        serializer = CommentSerializer(instance=comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)